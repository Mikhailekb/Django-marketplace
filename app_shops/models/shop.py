from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from imagekit.models import ProcessedImageField, ImageSpecField

from app_shops.models.discount import Discount


def get_shop_img_path(instance, name):
    return f'img/content/shops/{instance.shop.slug}/{name}'


class Shop(models.Model):
    """
    Модель магазина
    """
    name = models.CharField(max_length=256, verbose_name=_('name'))
    slug = AutoSlugField(max_length=70, unique=True, populate_from='name_en', verbose_name='URL')
    description = models.TextField(verbose_name=_('description'))
    phone = PhoneNumberField(null=False, blank=False, unique=True, verbose_name=_('phone number'))
    mail = models.EmailField(max_length=256, verbose_name=_('email'))
    address = models.CharField(max_length=1024, verbose_name=_('address'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('edited'))
    main_image = models.OneToOneField('ShopImage', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='main_for_shop')

    class Meta:
        verbose_name_plural = _('shops')
        verbose_name = _('shop')
        ordering = ['id']

    def __str__(self):
        return self.name


class ProductShop(models.Model):
    """
    Промежуточная модель, которая содержит информацию о количестве товара в магазине и цене
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='in_shops')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='with_products')
    count_left = models.IntegerField(default=0, verbose_name=_('left in shop'))
    count_sold = models.IntegerField(default=0, verbose_name=_('sold in shop'))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('price'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    active_discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL,
                                        related_name='product_in_shop')

    def __str__(self):
        return self.product.name


class ShopImage(models.Model):
    """
    Модель изображения для магазина
    """
    image = ProcessedImageField(upload_to=get_shop_img_path, options={'quality': 80})
    small = ImageSpecField(source='image', id='app_shops:thumbnail_200x200')
    middle = ImageSpecField(source='image', id='app_shops:thumbnail_500x500')
    large = ImageSpecField(source='image', id='app_shops:thumbnail_800x800')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='images', verbose_name=_('product'))
    uploaded = models.DateTimeField(auto_now_add=True, verbose_name=_('uploaded'))

    class Meta:
        verbose_name_plural = _('shop images')
        verbose_name = _('shop image')
        ordering = ['id']

    def __str__(self):
        return f'Image of shop: {self.shop.name}'