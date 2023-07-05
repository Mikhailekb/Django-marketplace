from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from phonenumber_field.modelfields import PhoneNumberField

from app_shops.models.shop import ProductShop


class Order(models.Model):
    """
    Модель заказа
    """

    ORDER_STATUS = (
        ('p', _('Paid')),
        ('np', _('Not paid')),
        ('d', _('Delivery type'))
    )

    buyer = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='orders',
                              verbose_name=_('buyer'))
    comment = models.TextField(max_length=500, null=True, blank=True, verbose_name=_('comment'))
    delivery_category = models.ForeignKey('DeliveryCategory', on_delete=models.PROTECT, related_name='items',
                                          verbose_name=_('delivery category'))
    name = models.CharField(max_length=100, verbose_name=_('name'))
    phone = PhoneNumberField(verbose_name=_('phone'))
    email = models.EmailField(verbose_name=_('email'))
    city = models.CharField(max_length=100, verbose_name=_('city'))
    address = models.TextField(max_length=256, verbose_name=_('address'))
    is_free_delivery = models.BooleanField(default=False, verbose_name=_('is free delivery'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))
    is_canceled = models.BooleanField(default=False, verbose_name=_('is canceled'))
    status = models.CharField(default='np', choices=ORDER_STATUS, max_length=2, verbose_name=_('order status'))

    def __str__(self):
        order = _('order')
        return f'{order.capitalize()} №{self.id}'

    class Meta:
        verbose_name_plural = _('orders')
        verbose_name = _('order')

    def get_absolute_url(self) -> str:
        return reverse('order_detail', kwargs={'pk': self.pk})


class OrderItem(models.Model):
    """
    Объект заказа
    """
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items', verbose_name=_('order'))
    product_shop = models.ForeignKey(ProductShop, on_delete=models.PROTECT, related_name='in_orders',
                                     verbose_name=_('product'))
    price_on_add_moment = MoneyField(max_digits=8, decimal_places=2, default_currency='RUB',
                                     verbose_name=_('price on add moment'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('quantity'))

    class Meta:
        verbose_name_plural = _('order items')
        verbose_name = _('order item')


class PaymentItem(models.Model):
    """
    Экземпляр оплаты
    """

    PAYMENT_CATEGORY = (
        ('bank-card', _('Bank card')),
        ('some-one', _('Some other way')),
    )

    IS_PASSED_CHOICES = (
        (True, _('Passed')),
        (False, _('Payment failed'))
    )

    order = models.OneToOneField(
        'Order', on_delete=models.CASCADE, related_name='payment_item', verbose_name=_('order'))
    payment_category = models.CharField(max_length=15, choices=PAYMENT_CATEGORY, verbose_name=_('category'))
    total_price = MoneyField(max_digits=10, null=True, decimal_places=2,
                             default_currency='RUB', verbose_name=_('total price'))
    from_account = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('from account'))
    is_passed = models.BooleanField(default=False, choices=IS_PASSED_CHOICES, verbose_name=_('is passed'))

    class Meta:
        verbose_name_plural = _('payment items')
        verbose_name = _('payment item')


class DeliveryCategory(models.Model):
    """
    Модель способа доставки
    """
    name = models.CharField(max_length=50, verbose_name=_('name'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    price = MoneyField(max_digits=8, decimal_places=2, default_currency='RUB', verbose_name=_('price'))
    codename = AutoSlugField(max_length=100, unique=True, populate_from='name_en', verbose_name=_('codename'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _('delivery categories')
        verbose_name = _('delivery category')
