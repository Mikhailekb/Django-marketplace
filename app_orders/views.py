from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from django.http import JsonResponse, HttpRequest, HttpResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView, DetailView
from djmoney.contrib.exchange.models import convert_money

from app_cart.cart import Cart
from app_shops.models.shop import ProductShop
from django_marketplace.constants import ORDER_AMOUNT_WHICH_DELIVERY_FREE
from .forms import OrderForm
from .models import DeliveryCategory, Order, OrderItem, PaymentItem, PaymentCategory


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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        goods = self._get_goods_in_cart(cart)

        total_price = cart.get_total_price()
        is_free_delivery = (
                total_price.amount >= ORDER_AMOUNT_WHICH_DELIVERY_FREE
                and all(goods[0].shop_id == item.shop_id for item in goods)
        )
        context['is_free_delivery'] = is_free_delivery
        return context

    @staticmethod
    def _get_goods_in_cart(cart):
        goods_id = cart.cart.keys()
        return ProductShop.objects.filter(id__in=goods_id)

    def form_valid(self, form):
        comment = form.cleaned_data.get('comment')
        is_free_delivery = form.cleaned_data.get('is_free_delivery', False)
        delivery_category: DeliveryCategory = form.cleaned_data.get('delivery_category')
        name = form.cleaned_data.get('name')
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email')
        city = form.cleaned_data.get('city')
        address = form.cleaned_data.get('address')
        order = Order(buyer=self.request.user, delivery_category=delivery_category, name=name,
                      phone=phone, email=email, city=city, address=address, comment=comment)

        cart = Cart(self.request)
        total_price = cart.get_total_price()
        if not is_free_delivery or delivery_category.codename != 'regular-delivery':
            total_price += delivery_category.price
            is_free_delivery = False

        goods, error_messages = self._check_count_left_goods(cart, order)
        if error_messages:
            form.errors['not_enough_goods'] = error_messages
            return super().form_invalid(form)

        order.is_free_delivery = is_free_delivery
        order.save()
        OrderItem.objects.bulk_create(goods)
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


def get_delivery_category_info(request):
    delivery_category_id = request.GET.get('delivery_category_id')
    try:
        delivery_category = DeliveryCategory.objects.get(id=delivery_category_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Delivery category does not exist"})

    price = (
        str(delivery_category.price)
        if request.LANGUAGE_CODE == 'ru'
        else str(convert_money(delivery_category.price, 'USD'))
    )
    response_data = {
        'title': delivery_category.name,
        'price': price,
        'codename': delivery_category.codename
    }
    return JsonResponse(response_data)


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
