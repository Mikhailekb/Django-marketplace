from collections import defaultdict
from decimal import Decimal
from random import sample
from typing import Any, Sequence

from django.contrib import messages
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import QuerySet, Avg, Min, Max, Sum, Prefetch, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django_filters.views import FilterView
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money

from app_cart.forms import CartAddProductForm
from django_marketplace.constants import TAGS_CACHE_LIFETIME, SALES_CACHE_LIFETIME
from .filters import ProductFilter
from .forms import ReviewForm
from .models.banner import Banner, SpecialOffer, SmallBanner
from .models.discount import Discount
from .models.product import SortProduct, Product, TagProduct, FeatureToProduct, Review
from .models.shop import ProductShop
from .services.functions import get_prices, price_exp, price_exp_banners


class HomeView(TemplateView):
    """
    Представление для отображения главной страницы
    """
    template_name = 'pages/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goods = Product.objects.select_related('category', 'main_image') \
            .prefetch_related(Prefetch('in_shops', queryset=ProductShop.objects.select_related('shop'))) \
            .annotate(Sum('in_shops__count_sold')).order_by('-in_shops__count_sold__sum')[:8]\
            .annotate(avg_price=Avg(price_exp))

        banners = Banner.objects.filter(is_active=True)[:3].select_related('product')

        small_banners = SmallBanner.objects.all()[:3].select_related('product').annotate(
            price_from=Min(price_exp_banners))
        if product_with_timer := SpecialOffer.objects.all().first():
            context['product_with_timer'] = ProductShop.objects.with_discount_price() \
                .get(id=product_with_timer.product_shop_id)
            context['date_end'] = product_with_timer.date_end.strftime('%d.%m.%Y %H:%M')

        context['top_goods'] = goods
        context['banners'] = banners
        context['small_banners'] = small_banners

        return context


class CatalogView(FilterView):
    """
    Представление для отображения страницы каталога
    """
    template_name = 'pages/catalog.html'
    context_object_name = 'goods'
    filterset_class = ProductFilter

    def get_paginate_by(self, queryset):
        self.paginate_by = 8
        if self.request.user_agent.is_mobile:
            self.paginate_by = 4
        elif self.request.user_agent.is_tablet:
            self.paginate_by = 6
        return self.paginate_by

    def get_queryset(self):
        filter_options = {'is_active': True, 'in_shops__is_active': True}
        if category := self.request.GET.get('category'):
            filter_options['category__slug'] = category

        self.queryset = Product.objects.filter(**filter_options) \
            .select_related('category', 'main_image') \
            .annotate(avg_price=Avg(price_exp),
                      min_price=Min(price_exp),
                      max_price=Max(price_exp),
                      count_sold=Sum('in_shops__count_sold'),
                      feedback=Count('reviews')).order_by('count_sold')

        return self.queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)

        self.ordering = self.filterset.data.get('order_by', 'count_sold')
        category = self.request.GET.get('category', default='')
        tags = cache.get_or_set('tags', TagProduct.objects.all(), timeout=TAGS_CACHE_LIFETIME)

        min_price, max_price, price_from, price_to = self._get_price_range()

        context['sort'] = SortProduct
        context['tags'] = tags
        context['order_by'] = self.ordering
        context['category'] = category
        context['price_from'] = price_from
        context['price_to'] = price_to
        context['min_price'] = min_price
        context['max_price'] = max_price
        context['form'] = self.filterset.form

        return context

    def _get_price_range(self) -> tuple[Decimal, Decimal, str, str]:
        price = self.filterset.data.get('price')
        aggregate: dict = self.queryset.aggregate(min=Min('min_price'), max=Max('max_price'))
        min_price = aggregate.get('min')
        max_price = aggregate.get('max')

        if price and len(price.split(';')) == 3 and all(item.isdigit() for item in price.split(';')[:2]):
            price_from, price_to, language_code = price.split(';')
        elif self.request.LANGUAGE_CODE == 'ru':
            price_from, price_to = min_price, max_price
        else:
            price_from = convert_money(Money(min_price, 'RUB'), 'USD').amount
            price_to = convert_money(Money(max_price, 'RUB'), 'USD').amount

        return min_price, max_price, price_from, price_to


class SaleView(ListView):
    """
    Представление для отображения страницы списка распродаж
    """
    template_name = 'pages/sale.html'
    context_object_name = 'sales'

    def get_queryset(self):
        self.queryset = cache.get_or_set('sales', Discount.objects
                                         .filter(is_active=True, date_start__lte=timezone.now())
                                         .select_related('main_image'), timeout=SALES_CACHE_LIFETIME)
        return self.queryset

    def get_paginate_by(self, queryset):
        self.paginate_by = 12
        if self.request.user_agent.is_tablet:
            self.paginate_by = 10
        elif self.request.user_agent.is_mobile:
            self.paginate_by = 8
        return self.paginate_by


class DiscountDetailView(DetailView):
    model = Discount
    template_name = 'pages/discount.html'
    context_object_name = 'discount'
    slug_url_kwarg = 'promo_slug'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object: Discount = self.get_object()
        if not self.object.is_active or self.object.date_start > timezone.now():
            return redirect('sales')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj: Discount = kwargs.get('object')
        goods = ProductShop.objects \
            .with_discount_price() \
            .filter(discount=obj) \
            .select_related('product__main_image', 'product__category') \
            .order_by('product__name')
        if date_end := obj.date_end:
            context['date_end'] = date_end.strftime('%d.%m.%Y %H:%M')

        paginate_by = 8
        if self.request.user_agent.is_mobile:
            paginate_by = 4
        elif self.request.user_agent.is_tablet:
            paginate_by = 6

        paginator = Paginator(goods, paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ClearCache(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_staff:
            raise PermissionError

        if 'product_cache' in request.POST:
            cache.delete('tags')
            messages.success(self.request, _('Cache cleared successfully'))
        elif 'categories_cache' in request.POST:
            cache.delete('categories')
            messages.success(self.request, _('Cache cleared successfully'))
        elif 'all_cache' in request.POST:
            cache.clear()
            messages.success(self.request, _('Cache cleared successfully'))
        else:
            messages.warning(self.request, _('Error. Cache not cleared'))

        return redirect(request.META.get('HTTP_REFERER'))


class ProductDetailView(DetailView):
    """
    Представление детальной страницы товара
    """
    model = Product
    slug_url_kwarg = 'product_slug'
    template_name = 'pages/product.html'
    context_object_name = 'product'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('category', 'main_image'). \
            prefetch_related('images', 'tags',
                             Prefetch('features', queryset=FeatureToProduct.objects.select_related('feature_name')
                                      .prefetch_related('values')),
                             Prefetch('in_shops', queryset=ProductShop.objects.select_related('shop')),
                             Prefetch('reviews', queryset=Review.objects.select_related('profile'))).annotate(avg_price=Avg(price_exp))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product: Product = context['product']
        discounts_query = ProductShop.objects.with_discount_price().select_related('shop').filter(product=product)
        reviews_count = product.reviews.count()
        shop_prices = get_prices(discounts_query)
        cart_product_form = CartAddProductForm()

        context['review_form'] = ReviewForm
        context['sellers'] = shop_prices
        context['reviews_count'] = reviews_count
        context['cart_product_form'] = cart_product_form
        context['random_product_id'] = sample(list(product.in_shops.filter(is_active=True)), 1)[0].id

        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        product = self.get_object()
        if not request.user.is_authenticated:
            return redirect('login')

        profile = request.user.profile
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = Review(product=product, profile=profile, text=form.cleaned_data.get('text'))
            review.save()
        return redirect('product-detail', product_slug=product.slug)

    @staticmethod
    def get_prices(discounts_query):
        shop_prices = {product_shop: {'price_old': product_shop.price.amount}
        if not product_shop.discount_price
        else {'price_old': product_shop.price.amount, 'price_new': product_shop.discount_price}
                       for product_shop in discounts_query}
        price_list = [price.get('price_new') or price.get('price_old')
                      for price in shop_prices.values()]

        price = float(sum([float(price) if not isinstance(price, Money) else float(price.amount)
                           for price in price_list]) / len(price_list))

        return shop_prices, price


class ComparisonView(TemplateView):
    MAX_VALUE = 3
    template_name = 'pages/comparison.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comparison_products = self.request.session.get(
            'comparison_products', default=[])[:3]
        if comparison_products and isinstance(comparison_products, list) and len(comparison_products) <= self.MAX_VALUE:
            goods: QuerySet[Product] = Product.objects.filter(id__in=comparison_products) \
                .annotate(avg_price=Avg(price_exp)) \
                .select_related('category', 'main_image')

            if len({item.category_id for item in goods}) == 1:
                allowable_feature_names = self._get_allowable_feature_names(
                    context, comparison_products)

                comparison_list: QuerySet[Product] = goods.prefetch_related(
                    Prefetch('features', queryset=FeatureToProduct.objects.order_by('feature_name')
                             .select_related('feature_name')
                             .prefetch_related('values')
                             .filter(feature_name_id__in=allowable_feature_names)))

                context['comparison_list'] = comparison_list
                context['one_category'] = True
            else:
                context['comparison_list'] = goods
        return context

    def _get_allowable_feature_names(self, context: dict[str, Any], goods: Sequence) -> Sequence:
        """
        Метод, в котором происходит получение допустимых характеристик.
        Допустимыми являются те, которые встречаются у всех товаров из QuerySet.
        Также если is_difference = True, то исключается такое название характеристики,
        у которого идентичные значения у всех товаров из QuerySet.
        """
        is_difference = self.request.GET.get('is_difference')
        if is_difference == 'True':
            name_btn = _('Show all characteristics')
            is_difference_value = 'False'
            values = FeatureToProduct.objects.filter(product_id__in=goods) \
                .values('product_id', 'feature_name') \
                .annotate(values=ArrayAgg('values')) \
                .order_by('product_id', 'feature_name')
            result = {}
            for item in values:
                product_id = item['product_id']
                feature_name = item['feature_name']
                value = item['values']
                if product_id in result:
                    result[product_id][feature_name] = value
                else:
                    result[product_id] = {feature_name: value}

            common_keys = set.intersection(*[set(d.keys()) for d in result.values()])
            intersection_feature = {k: {key: value for key, value in v.items() if key in common_keys}
                                    for k, v in result.items()}

            value_dict = defaultdict(set)
            for v in intersection_feature.values():
                for feature_name_id, value in v.items():
                    value_dict[feature_name_id].add(value[0])

            value_dict = {k: v for k, v in value_dict.items() if len(v) > 1}
            allowable_feature_names = value_dict.keys()
        else:
            name_btn = _('Only differing characteristics')
            is_difference_value = 'True'

            allowable_feature_names = FeatureToProduct.objects.filter(product_id__in=goods) \
                .values('feature_name') \
                .annotate(count=Count('product_id')) \
                .filter(count=len(goods)) \
                .values_list('feature_name_id', flat=True, named=False)

        context['name_btn'] = name_btn
        context['is_difference_value'] = is_difference_value
        return allowable_feature_names

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        current_page = request.META.get('HTTP_REFERER')
        comparison_products = request.session.get('comparison_products', default=[])
        if product_id := request.POST.get('add_product'):
            if len(comparison_products) <= self.MAX_VALUE and product_id in comparison_products:
                return redirect(current_page)
            comparison_products.append(product_id)
        elif product_id := request.POST.get('delete_product'):
            if not isinstance(comparison_products, list) or product_id not in comparison_products:
                return redirect(current_page)
            comparison_products.remove(product_id)
        elif request.POST.get('delete_all'):
            request.session['comparison_products'] = comparison_products.clear()
        else:
            return redirect(current_page)

        request.session['comparison_products'] = comparison_products
        return redirect(current_page)


class OrderView(UserPassesTestMixin, FormView):
    """
    Представление для отображения страницы оформления заказа
    """
    form_class = OrderForm
    template_name = 'pages/order.html'

    def test_func(self) -> bool:
        user = self.request.user
        session = self.request.session
        return user.is_authenticated and session.get('cart')

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        initial['name'] = user.profile.name
        initial['phone'] = user.profile.phone
        initial['email'] = user.email
        return initial

    def form_valid(self, form):
        comment = form.cleaned_data.get('comment')

        delivery_category: DeliveryCategory = form.cleaned_data.get('delivery_category')
        name = form.cleaned_data.get('name')
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email')
        city = form.cleaned_data.get('city')
        address = form.cleaned_data.get('address')

        cart = Cart(self.request)
        order = Order.objects.create(buyer=self.request.user, delivery_category=delivery_category, name=name,
                                     phone=phone, email=email, city=city, address=address, comment=comment)

        goods, error_messages = self._check_count_left_goods(cart, order)

        if error_messages:
            form.errors['not_enough_goods'] = error_messages
            return super().form_invalid(form)

        OrderItem.objects.bulk_create(goods)

        total_price = cart.get_total_price()
        payment_category: PaymentCategory = form.cleaned_data.get('payment_category')
        PaymentItem.objects.create(order=order, payment_category=payment_category, total_price=total_price)

        self.request.session['order'] = order.id

        if payment_category.codename == 'bank-card':
            self.success_url = reverse_lazy('payment')
        elif payment_category.codename == 'some-other-way':
            self.success_url = reverse_lazy('home')
        return super().form_valid(form)

    @staticmethod
    def _check_count_left_goods(cart, order):
        goods = []
        error_messages = []
        for product_shop_id, values in cart.cart.items():
            if product_shop := ProductShop.objects.filter(id=product_shop_id, is_active=True).get():
                price = values.get('price')
                quantity = values.get('quantity')
                if product_shop.count_left - quantity < 0:
                    not_valid = True
                    name = product_shop.product.name
                    message = _(f"{name}: in stock - {product_shop.count_left}, in cart - {quantity}")
                    error_messages.append(message)
                else:
                    item = OrderItem(order=order, product_shop_id=product_shop_id,
                                     price_on_add_moment=price, quantity=quantity)
                    goods.append(item)
        return goods, error_messages


class PaymentView(UserPassesTestMixin, TemplateView):
    """
    Представление страницы оплаты заказа банковской картой
    """
    template_name = 'pages/paymentsomeone.html'

    def test_func(self) -> bool:
        user = self.request.user
        session = self.request.session
        return user.is_authenticated and session.get('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if order_id := self.request.session.get('order'):
            context['total_price'] = PaymentItem.objects.get(order_id=order_id).total_price
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        request.session.pop('cart', None)

        account: str = request.POST.get('numero1', None)
        if len(account) != 9:
            return redirect(reverse('home'))
        last_sym = account[-1:]

        order_id = self.request.session.get('order', None)
        payment = PaymentItem.objects.get(order_id=order_id)
        payment.from_account = account
        order: Order = Order.objects.get(id=order_id)

        if last_sym.isdigit() and int(last_sym) % 2 == 0:
            payment.is_passed = True
            payment.order_status = 'p'
            order.is_paid = True

            products_to_update = []
            for order_item in order.items.all():
                quantity = order_item.quantity
                product_shop = order_item.product_shop

                product_shop.count_left -= quantity
                product_shop.count_sold += quantity

                products_to_update.append(product_shop)
            ProductShop.objects.bulk_update(products_to_update, ['count_left', 'count_sold'])

        payment.save()
        order.save()
        return redirect(reverse('payment_progress'))


class ProgressPaymentView(UserPassesTestMixin, TemplateView):
    """
    Представление страницы ожидания ответа от сервиса оплаты
    """
    template_name = 'pages/progressPayment.html'

    def test_func(self) -> bool:
        user = self.request.user
        session = self.request.session
        return user.is_authenticated and session.get('order') and session.get('cart') is None


class OrderDetailView(UserPassesTestMixin, DetailView):
    """
    Представление детальной страницы заказа
    """
    template_name = 'pages/oneorder.html'
    model = Order
    context_object_name = 'order'

    def test_func(self) -> bool:
        user = self.request.user
        self.object = self.get_object()
        buyer_id = self.object.buyer_id

        return (buyer_id == user.id and self.object.payment_item.from_account) or user.is_staff

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = Order.objects.filter(pk=pk).select_related('delivery_category', 'payment_item').prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related(
                'product_shop', 'product_shop__product', 'product_shop__product__main_image')))

        try:
            self.object = queryset.get()
        except queryset.model.DoesNotExist as e:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {'verbose_name': queryset.model._meta.verbose_name}
            ) from e

        return self.object

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = OrderForm
        context['order'] = self.object

        if self.object.payment_item.is_passed:
            self.request.session.pop('order', None)
        else:
            self.request.session['order'] = self.object.id
        return context
