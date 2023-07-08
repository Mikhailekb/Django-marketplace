from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Prefetch, QuerySet
from django.http import JsonResponse, HttpRequest, HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView, DetailView
from djmoney.contrib.exchange.models import convert_money

from app_cart.cart import Cart
from app_shops.models.shop import ProductShop
from app_shops.services.functions import get_object_or_none
from django_marketplace.constants import ORDER_AMOUNT_WHICH_DELIVERY_FREE
from .forms import OrderForm
from .models import DeliveryCategory, Order, OrderItem, PaymentItem


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

        total_price = cart.get_total_price_rub()
        is_free_delivery = (
                total_price.amount >= ORDER_AMOUNT_WHICH_DELIVERY_FREE
                and all(goods[0].shop_id == item.shop_id for item in goods)
        )
        context['is_free_delivery'] = is_free_delivery
        return context

    @staticmethod
    def _get_goods_in_cart(cart: Cart) -> QuerySet[ProductShop]:
        goods_id = cart.cart.keys()
        return ProductShop.objects.filter(id__in=goods_id)

    def form_valid(self, form: OrderForm):
        is_free_delivery = form.cleaned_data.get('is_free_delivery', False)
        cart = Cart(self.request)
        total_price = cart.get_total_price_rub()
        delivery_category: DeliveryCategory = form.cleaned_data.get('delivery_category')

        if not is_free_delivery or delivery_category.codename != 'regular-delivery':
            total_price += delivery_category.price
            is_free_delivery = False

        order = self._make_order(form)

        goods, error_messages = self._check_count_left_goods(cart, order)
        if error_messages:
            form.errors['not_enough_goods'] = error_messages
            return super().form_invalid(form)

        order.is_free_delivery = is_free_delivery
        order.save()
        OrderItem.objects.bulk_create(goods)
        payment_category = form.cleaned_data.get('payment_category')
        PaymentItem.objects.create(order=order, payment_category=payment_category, total_price=total_price)

        self.request.session['order'] = order.id

        self._set_success_url(payment_category)
        return super().form_valid(form)

    def _make_order(self, form):
        comment = form.cleaned_data.get('comment')
        delivery_category: DeliveryCategory = form.cleaned_data.get('delivery_category')
        name = form.cleaned_data.get('name')
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email')
        city = form.cleaned_data.get('city')
        address = form.cleaned_data.get('address')
        order = Order(buyer=self.request.user, delivery_category=delivery_category, name=name,
                      phone=phone, email=email, city=city, address=address, comment=comment)
        return order

    def _set_success_url(self, payment_category):
        if payment_category == 'bank-card':
            self.success_url = reverse_lazy('payment-bank-card')
        elif payment_category == 'some-one':
            self.success_url = reverse_lazy('payment-some-one')
        else:
            self.success_url = reverse_lazy('home')

    @staticmethod
    def _check_count_left_goods(cart: Cart, order: Order) -> tuple[list[OrderItem], list]:
        goods = []
        error_messages = []
        for product_shop_id, values in cart.cart.items():
            product_shop = get_object_or_none(ProductShop, id=product_shop_id)
            if not product_shop:
                continue

            name = product_shop.product.name
            if product_shop.is_active is False:
                message = _(f"{name} is not active product")
                error_messages.append(message)

            price = values.get('price')
            quantity = values.get('quantity')
            if product_shop.count_left - quantity < 0:
                message = _(f"{name}: in stock - {product_shop.count_left}, in cart - {quantity}")
                error_messages.append(message)
            else:
                item = OrderItem(order=order, product_shop_id=product_shop_id,
                                 price_on_add_moment=price, quantity=quantity)
                goods.append(item)
        return goods, error_messages


def get_delivery_category_info(request: HttpRequest, pk: int) -> JsonResponse:
    delivery_category = get_object_or_404(DeliveryCategory, pk=pk)

    price = (
        str(delivery_category.price) if request.LANGUAGE_CODE == 'ru'
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
    template_name = 'pages/payment.html'

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

        account: str = request.POST.get('account_number')
        if not account or len(account) != 9:
            return redirect(reverse('home'))
        last_sym = account[-1:]

        order_id = self.request.session.get('order', None)
        payment = PaymentItem.objects.get(order_id=order_id)
        payment.from_account = account
        order: Order = Order.objects.get(id=order_id)

        if last_sym.isdigit() and int(last_sym) % 2 == 0:
            payment.is_passed = True
            order.status = 'p'

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


class PaymentSomeOneView(PaymentView):
    template_name = 'pages/paymentsomeone.html'


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
        self.get_object()
        buyer_id = self.object.buyer_id

        return (buyer_id == user.id and self.object.payment_item.from_account) or user.is_staff

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = Order.objects.filter(pk=pk).select_related('delivery_category', 'payment_item').prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related(
                'product_shop', 'product_shop__product', 'product_shop__product__main_image')))

        try:
            self.object = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_('No order found matching the query'))

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
            items: QuerySet[OrderItem] = self.object.items.all()
            if all(item.product_shop.is_active for item in items):
                context['can_pay'] = True
                payment_page = f'payment-{self.object.payment_item.payment_category}'
                context['payment_page'] = payment_page
                self.request.session['order'] = self.object.id
            else:
                self.request.session.pop('order', None)
        return context
