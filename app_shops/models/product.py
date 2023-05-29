from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField, ImageSpecField
from app_shops.services import img_processors

def get_good_img_path(instance, name):
    return f'img/content/products/{instance.product.slug}/{name}'

class SortProduct(models.Model):
    css_cls = [
        (0, ''),
        (1, 'Sort-sortBy_dec'),
        (2, 'Sort-sortBy_inc')]

    name = models.CharField(max_length=100, verbose_name=_('name'))
    sort_field = models.CharField(max_length=100, verbose_name=_('sort field'))

    def __str__(self):
        return self.name


class TagProduct(models.Model):
    codename = AutoSlugField(max_length=100, verbose_name=_('codename'), unique=True, populate_from='name_en')
    name = models.CharField(max_length=100, verbose_name=_('name'))
    goods = models.ManyToManyField('Product', related_name='tags', verbose_name=_('goods'), blank=True)

    class Meta:
        verbose_name_plural = _('tags')
        verbose_name = _('tag')

    def __str__(self):
        return self.name


class FeatureName(models.Model):
    """
    Модель имени характеристики товаров
    """
    name = models.CharField(max_length=100, verbose_name=_('name'))

    def __str__(self):
        return self.name


class Feature(models.Model):
    """
    Модель характеристики товара
    """
    name = models.ForeignKey(FeatureName, on_delete=models.CASCADE, verbose_name=_('name'),
                             related_name='feature_value')
    value = models.CharField(max_length=100, verbose_name=_('value'))

    def __str__(self):
        return f'{self.name}: {self.value}'


class Product(models.Model):
    """
    Модель товара
    """
    name = models.CharField(max_length=256, verbose_name=_('name'))
    slug = AutoSlugField(max_length=70, unique=True, populate_from='name_en', verbose_name='URL')
    description_short = models.TextField(verbose_name=_('description short'))
    description_long = models.TextField(verbose_name=_('description long'))
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', verbose_name=_('products'))
    sellers = models.ManyToManyField('Shop', through='ProductShop')
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))
    main_image = models.OneToOneField('ProductImage', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='main_for_product')
    features = models.ManyToManyField('Feature', verbose_name=_('features'), blank=True, related_name='goods')

    class Meta:
        verbose_name_plural = _('products')
        verbose_name = _('product')

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """
    Модель изображения для товара
    """
    image = ProcessedImageField(upload_to=get_good_img_path, options={'quality': 80})
    small = ImageSpecField(source='image', id='app_shops:thumbnail_200x200')
    middle = ImageSpecField(source='image', id='app_shops:thumbnail_500x500')
    large = ImageSpecField(source='image', id='app_shops:thumbnail_800x800')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_('product'))
    uploaded = models.DateTimeField(auto_now_add=True, verbose_name=_('uploaded'))

    class Meta:
        verbose_name_plural = _('product images')
        verbose_name = _('product image')

    def __str__(self):
        return f'Image of product: {self.product.name}'
