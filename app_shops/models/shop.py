from autoslug import AutoSlugField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case, When, F
from django.db.models.functions import Greatest
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from imagekit.models import ProcessedImageField, ImageSpecField
from phonenumber_field.modelfields import PhoneNumberField

from app_shops.models.discount import Discount


def get_shop_img_path(instance, name) -> str:
    """Возвращает путь для хранения изображений данного магазина"""
    return f'img/content/shops/{instance.shop.slug}/{name}'


class Shop(models.Model):
    """
    Модель магазина
    """
    name = models.CharField(max_length=120, verbose_name=_('name'))
    slug = AutoSlugField(max_length=70, unique=True, populate_from='name_en', verbose_name='URL')
    description = models.TextField(verbose_name=_('description'))
    phone = PhoneNumberField(null=False, blank=False, unique=True, verbose_name=_('phone number'))
    mail = models.EmailField(max_length=256, verbose_name=_('email'))
    address = models.CharField(max_length=1024, verbose_name=_('address'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('edited'))
    main_image = models.OneToOneField('ShopImage', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='main_for_shop', verbose_name=_('main image'))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = _('shops')
        verbose_name = _('shop')


class ProductShopManager(models.Manager):
    """
    Менеджер для ProductShop, добавляющий метод вычисления цены со скидкой
    """
    def with_discount_price(self):
        min_cost_expression = Case(
            When(discount__is_active=False,
                 then=None),
            When(discount__min_cost__isnull=False,
                 then=F('discount__min_cost'))
        )
        price_expression = Case(
            When(discount__is_active=False,
                 then=None),
            When(discount__discount_percentage__isnull=False,
                 then=F('price') - F('price') * F('discount__discount_percentage') / 100),
            When(discount__discount_amount__isnull=False,
                 then=F('price') - F('discount__discount_amount')),
            output_field=MoneyField()
        )
        discount_price_expression = Greatest(price_expression, min_cost_expression)
        return self.annotate(discount_price=discount_price_expression)


class ProductShop(models.Model):
    """
    Промежуточная модель, которая содержит информацию о количестве товара в магазине и цене
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='in_shops')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='with_products')
    count_left = models.IntegerField(default=0, verbose_name=_('left in shop'))
    count_sold = models.IntegerField(default=0, verbose_name=_('sold in shop'))
    price = MoneyField(max_digits=8, decimal_places=2, default_currency='RUB', verbose_name=_('price'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name='product_in_shop')

    objects = ProductShopManager()

    def __str__(self) -> str:
        return self.product.name

    class Meta:
        unique_together = ('product', 'shop')

    def clean(self):
        if self.discount_id:
            min_cost = Discount.objects.get(
                id=self.discount_id).min_cost      # обращение self.discount.min_cost вызывает исключение
            if min_cost and self.price <= min_cost:
                raise ValidationError(
                    {'price': _('The price cannot be less than the minimum specified in the discount')}
                )


class ShopImage(models.Model):
    """
    Модель изображения для магазина
    """
    image = ProcessedImageField(upload_to=get_shop_img_path, options={'quality': 80}, verbose_name=_('image'))
    small = ImageSpecField(source='image', id='app_shops:thumbnail_200x200')
    middle = ImageSpecField(source='image', id='app_shops:thumbnail_500x500')
    large = ImageSpecField(source='image', id='app_shops:thumbnail_800x800')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='images', verbose_name=_('shop'))
    uploaded = models.DateTimeField(auto_now_add=True, verbose_name=_('uploaded'))

    def __str__(self) -> str:
        return f'Image of shop: {self.shop.name}'

    class Meta:
        verbose_name_plural = _('shop images')
        verbose_name = _('shop image')
