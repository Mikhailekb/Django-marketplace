from collections import defaultdict
from decimal import Decimal
from typing import Any, Sequence

from django.contrib.auth.decorators import login_required
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import QuerySet, Avg, Min, Max, Sum, Prefetch, Count
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, ListView, DetailView
from django_filters.views import FilterView
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money

from app_cart.forms import CartAddProductForm
from django_marketplace.constants import TAGS_CACHE_LIFETIME, SALES_CACHE_LIFETIME, SHOPS_CACHE_LIFETIME, \
    PRODUCTS_TOP_CACHE_LIFETIME
from .filters import ProductFilter
from .forms import ReviewForm
from .models.banner import Banner, SpecialOffer, SmallBanner, SliderBanner
from .models.discount import Discount
from .models.product import Product, TagProduct, FeatureToProduct, Review, ViewHistory
from .models.shop import ProductShop, Shop
from .services.functions import get_prices, price_exp, price_exp_banners
from .templatetags.custom_filters import random_related_id
from django.urls import reverse


class HomeView(TemplateView):
    """
    Представление для отображения главной страницы
    """
    template_name = 'pages/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goods = Product.objects \
                    .filter(is_active=True, in_shops__is_active=True) \
                    .select_related('category', 'main_image') \
                    .annotate(sum_count_sold=Sum('in_shops__count_sold'),
                              avg_price=Avg(price_exp),
                              in_shops_id=ArrayAgg('in_shops')) \
                    .order_by('-sum_count_sold')[:8]

        banners = Banner.objects \
                      .filter(is_active=True) \
                      .select_related('product')[:3]

        small_banners = SmallBanner.objects \
                            .select_related('product') \
                            .annotate(price_from=Min(price_exp_banners))[:3]

        if product_with_timer := SpecialOffer.objects.all().first():
            context['product_with_timer'] = ProductShop.objects.with_discount_price() \
                .get(id=product_with_timer.product_shop_id)
            context['date_end'] = product_with_timer.date_end.strftime('%d.%m.%Y %H:%M')

        slider_items = SliderBanner.objects.select_related('product', 'product__category', 'product__main_image') \
            .annotate(avg_price=Avg(price_exp_banners),
                      in_shops_id=ArrayAgg('product__in_shops'))

        context['top_goods'] = goods
        context['banners'] = banners
        context['small_banners'] = small_banners
        context['slider_items'] = slider_items

        return context


class CatalogView(FilterView):
    """
    Представление для отображения страницы каталога
    """
    template_name = 'pages/catalog.html'
    context_object_name = 'goods'
    filterset_class = ProductFilter

    PRODUCT_SORTED = (('count_sold', _('Popularity')), ('avg_price', _('Cost')),
                      ('created', _('Novelty')), ('feedback', _('Feedback')))

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
                      feedback=Count('reviews'),
                      in_shops_id=ArrayAgg('in_shops')).order_by('count_sold')

        return self.queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)

        self.ordering = self.filterset.data.get('order_by', 'count_sold')
        category = self.request.GET.get('category', default='')
        tags = cache.get_or_set('tags', TagProduct.objects.all(), timeout=TAGS_CACHE_LIFETIME)

        min_price, max_price, price_from, price_to = self._get_price_range()

        context['sort'] = self.PRODUCT_SORTED
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
        elif min_price:
            price_from = convert_money(Money(min_price, 'RUB'), 'USD').amount
            price_to = convert_money(Money(max_price, 'RUB'), 'USD').amount
        else:
            price_from, price_to = 0, 0

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
            .filter(discount=obj, is_active=True) \
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
        queryset = queryset.select_related('category', 'main_image') \
            .prefetch_related('images', 'tags',
                              Prefetch('features', queryset=FeatureToProduct.objects.select_related('feature_name')
                                       .prefetch_related('values')),
                              Prefetch('in_shops', queryset=ProductShop.objects.select_related('shop')),
                              Prefetch('reviews', queryset=Review.objects.select_related('profile'))) \
            .annotate(avg_price=Avg(price_exp), in_shops_id=ArrayAgg('in_shops'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product: Product = context['product']
        discounts_query = ProductShop.objects.with_discount_price().select_related('shop') \
            .filter(product=product, is_active=True)
        reviews_count = product.reviews.count()
        shop_prices = get_prices(discounts_query)
        cart_product_form = CartAddProductForm()
        self._add_product_to_viewed(product)

        context['review_form'] = ReviewForm
        context['sellers'] = shop_prices
        context['reviews_count'] = reviews_count
        context['cart_product_form'] = cart_product_form
        context['random_product_id'] = random_related_id(product)
        return context

    @method_decorator(login_required)
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        product = self.get_object()
        profile = request.user.profile
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = Review(product=product, profile=profile, text=form.cleaned_data.get('text'))
            review.save()
        return redirect('product-detail', product_slug=product.slug)

    def _add_product_to_viewed(self, product):
        if self.request.user.is_authenticated:
            profile = self.request.user.profile
            self._delete_product_from_history(product, profile)
            ViewHistory(profile=profile, product=product).save()

    @staticmethod
    def _delete_product_from_history(product, profile):
        history = ViewHistory.objects.select_related('product', 'profile') \
            .filter(profile=profile).order_by('-date_viewed')
        product_in_history = [obj.product for obj in history]
        if product in product_in_history:
            ViewHistory.objects.filter(profile=profile, product=product).delete()

        history_list = list(history)
        while len(history_list) >= 20:
            record_to_delete = history_list.pop(-1)
            ViewHistory.objects.filter(id=record_to_delete.id).delete()


class ComparisonView(TemplateView):
    template_name = 'pages/comparison.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comparison_products = self.request.session.get(
            'comparison_products', default=[])[:3]
        if comparison_products and isinstance(comparison_products, list):
            goods: QuerySet[Product] = Product.objects.filter(id__in=comparison_products) \
                .annotate(avg_price=Avg(price_exp),
                          in_shops_id=ArrayAgg('in_shops')) \
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
            context['count_item'] = goods.count()
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
            result_list = list(result.values())
            difference_features = {}

            for a in range(len(result_list)):
                for key, value in result_list[0].items():
                    if key in result_list[a] and value != result_list[a][key]:
                        difference_features[key] = value

            allowable_feature_names = difference_features.keys()
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
        current_page = request.META.get('HTTP_REFERER', reverse('catalog'))
        comparison_products = request.session.get('comparison_products', default=[])
        if product_id := request.POST.get('add_product'):
            if product_id in comparison_products:
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


class AboutUsView(TemplateView):
    template_name = 'pages/about.html'


class ShopDetailView(DetailView):
    """
    Представление детальной страницы продавца
    """
    template_name = 'pages/shop.html'
    slug_url_kwarg = 'store_slug'
    context_object_name = 'shop'

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)
        try:
            shop = cache.set(f'shop_{slug}',
                             Shop.objects.select_related('main_image')
                             .get(slug=slug),
                             timeout=SHOPS_CACHE_LIFETIME)
            return shop
        except ObjectDoesNotExist as e:
            raise Http404(_('No shop found matching the query')) from e

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get(self.slug_url_kwarg)
        products_top = cache.get_or_set(f'products_top_{slug}',
                                        ProductShop.objects
                                        .with_discount_price()
                                        .filter(shop__slug=slug)
                                        .select_related('product__category', 'product__main_image')
                                        .order_by('-count_sold')[:10],
                                        timeout=PRODUCTS_TOP_CACHE_LIFETIME)
        context['goods'] = products_top

        return context
