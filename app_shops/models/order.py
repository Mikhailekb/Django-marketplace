from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField


class Order(models.Model):
    """
    Модель заказа
    """
    buyer = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='orders', verbose_name=_('buyer'))
    comment = models.TextField(max_length=500, verbose_name=_('comment'))
    is_paid = models.BooleanField(default=False, verbose_name=_('is paid'))
    is_confirmed = models.BooleanField(default=False, verbose_name=_('is confirmed'))
    is_canceled = models.BooleanField(default=False, verbose_name=_('is canceled'))

    class Meta:
        verbose_name_plural = _('orders')
        verbose_name = _('order')


class OrderItem(models.Model):
    """
    Объект заказа
    """
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items', verbose_name=_('order'))
    product = models.ForeignKey('ProductShop', on_delete=models.CASCADE, related_name='in_orders',
                                verbose_name=_('product'))
    price_on_add_moment = MoneyField(max_digits=8, decimal_places=2, default_currency='RUB',
                                     verbose_name=_('price on add moment'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('quantity'))

    class Meta:
        verbose_name_plural = _('order items')
        verbose_name = _('order item')


class PaymentCategory(models.Model):
    """
    Модель способа оплаты
    """
    name = models.CharField(max_length=50, verbose_name=_('name'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    codename = AutoSlugField(max_length=100, verbose_name=_('codename'), unique=True, populate_from='name_en')

    class Meta:
        verbose_name_plural = _('payment categories')
        verbose_name = _('payment category')

    def __str__(self):
        return self.name


class PaymentItem(models.Model):
    """
    Экземпляр оплаты
    """
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment_items', verbose_name=_('order'))
    category = models.ForeignKey('PaymentCategory', on_delete=models.CASCADE, related_name='items',
                                 verbose_name=_('category'))
    from_card_account = models.CharField(max_length=50, verbose_name=_('from card account'))
    is_passed = models.BooleanField(default=False, verbose_name=_('is passed'))

    class Meta:
        verbose_name_plural = _('payment items')
        verbose_name = _('payment item')


class DeliveryCategory(models.Model):
    """
    Модель способа доставки
    """
    name = models.CharField(max_length=50, verbose_name=_('name'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    codename = AutoSlugField(max_length=100, verbose_name=_('codename'), unique=True, populate_from='name_en')


    class Meta:
        verbose_name_plural = _('delivery categories')
        verbose_name = _('delivery category')

    def __str__(self):
        return self.name


class DeliveryItem(models.Model):
    """
    Экземпляр доставки
    """
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='delivery_items', verbose_name=_('order'))
    category = models.ForeignKey('DeliveryCategory', on_delete=models.CASCADE, related_name='items',
                                 verbose_name=_('category'))
    city = models.CharField(max_length=256, verbose_name=_('city'))
    address = models.TextField(max_length=256, verbose_name=_('address'))

    class Meta:
        verbose_name_plural = _('delivery items')
        verbose_name = _('delivery item')
