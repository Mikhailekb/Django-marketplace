from autoslug import AutoSlugField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from uuslug import slugify
from phonenumber_field.modelfields import PhoneNumberField
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFit


def get_latin_name(instance):
    return slugify(instance.name)


def get_good_img_path(instance):
    return f'img/content/products/{instance.product.slug}/'


def get_shop_img_path(instance):
    return f'img/content/shops/{instance.shop.slug}/'


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    slug = AutoSlugField(max_length=70, verbose_name='URL', unique=True, populate_from='name_en')
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='child_category', verbose_name=_('parent category'))
    icon = models.FileField(upload_to='img/icons/departments/', null=True, blank=True, verbose_name=_('icon'),
                              validators=[FileExtensionValidator(['svg'])])

    class Meta:
        verbose_name_plural = _('categories')
        verbose_name = _('category')
        ordering = ['id']

    def __str__(self):
        if not self.parent:
            return self.name
        return f'{self.name} ({self.parent})'


class Product(models.Model):
    """
    Модель товара
    """
    name = models.CharField(max_length=256, verbose_name=_('name'))
    slug = AutoSlugField(max_length=70, unique=True, populate_from=get_latin_name, verbose_name=_('URL'))
    description = models.TextField(verbose_name=_('description'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name=_('products'))
    salers = models.ManyToManyField('Shop', through='ProductShop')
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))

    class Meta:
        verbose_name_plural = _('products')
        verbose_name = _('product')
        ordering = ['id']

    def __str__(self):
        return self.name


class Shop(models.Model):
    """
    Модель магазина
    """
    name = models.CharField(max_length=256, verbose_name=_('name'))
    slug = AutoSlugField(max_length=70, unique=True, populate_from=get_latin_name, verbose_name=_('URL'))
    description = models.TextField(verbose_name=_('description'))
    phone = PhoneNumberField(null=False, blank=False, unique=True, verbose_name=_('phone number'))
    mail = models.EmailField(max_length=256, verbose_name=_('email'))
    address = models.CharField(max_length=1024, verbose_name=_('address'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('edited'))

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_shops')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='with_products')
    count_left = models.IntegerField(default=0, verbose_name=_('left in shop'))
    count_sold = models.IntegerField(default=0, verbose_name=_('sold in shop'))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('price'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))

class ProductImage(models.Model):
    """Модель изображения для товара"""
    image = ProcessedImageField(upload_to=get_good_img_path, options={'quality': 80})
    small = ImageSpecField(source='image', id='app_shops:thumbnail_200x200', verbose_name=_('image small'))
    middle = ImageSpecField(source='image', id='app_shops:thumbnail_500x500', verbose_name=_('image middle'))
    large = ImageSpecField(source='image', id='app_shops:thumbnail_800x800', verbose_name=_('image large'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_('product'))
    uploaded = models.DateTimeField(auto_now_add=True, verbose_name=_('uploaded'))
    is_main = models.BooleanField(default=False, verbose_name=_('is main'))

    class Meta:
        verbose_name_plural = _('product images')
        verbose_name = _('product image')
        ordering = ['id']

    def __str__(self):
        return f'Image of product: {self.product.name}'


class ShopImage(models.Model):
    """Модель изображения для магазина"""
    image = ProcessedImageField(upload_to=get_shop_img_path, options={'quality': 80})
    small = ImageSpecField(source='image', id='app_shops:thumbnail_200x200', verbose_name=_('image small'))
    middle = ImageSpecField(source='image', id='app_shops:thumbnail_500x500', verbose_name=_('image middle'))
    large = ImageSpecField(source='image', id='app_shops:thumbnail_800x800', verbose_name=_('image large'))
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='images', verbose_name=_('product'))
    uploaded = models.DateTimeField(auto_now_add=True, verbose_name=_('uploaded'))
    is_main = models.BooleanField(default=False, verbose_name=_('is main'))

    class Meta:
        verbose_name_plural = _('shop images')
        verbose_name = _('shop image')
        ordering = ['id']

    def __str__(self):
        return f'Image of shop: {self.shop.name}'
