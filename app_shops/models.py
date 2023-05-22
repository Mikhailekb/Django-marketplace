from autoslug import AutoSlugField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from uuslug import slugify
from phonenumber_field.modelfields import PhoneNumberField
from imagekit.models import ProcessedImageField, ImageSpecField
from .services import img_processors
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions



def get_latin_name(instance):
    return slugify(instance.name)


def get_good_img_path(instance, name):
    return f'img/content/products/{instance.product.slug}/{name}'


def get_shop_img_path(instance, name):
    return f'img/content/shops/{instance.shop.slug}/{name}'


def get_banner_img_path(instance, name):
    return f'img/content/banners/{instance.product.slug}/{name}'





class Category(models.Model):
    """
    Модель категории товаров
    """
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

    def get_absolute_url(self):
        catalog_url = reverse('catalog')
        return f'{catalog_url}?category={self.slug}'


class SortProduct(models.Model):
    css_cls = [
        (0, ''),
        (1, 'Sort-sortBy_dec'),
        (2, 'Sort-sortBy_inc')]

    name = models.CharField(max_length=100, verbose_name=_('name'))
    sort_field = models.CharField(max_length=100, verbose_name=_('sort field'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class TagProduct(models.Model):
    codename = AutoSlugField(max_length=100, verbose_name=_('codename'), unique=True, populate_from='name_en')
    name = models.CharField(max_length=100, verbose_name=_('name'))
    goods = models.ManyToManyField('Product', related_name='tags', verbose_name=_('goods'), blank=True)

    class Meta:
        verbose_name_plural = _('tags')
        verbose_name = _('tag')

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Модель товара
    """
    name = models.CharField(max_length=256, verbose_name=_('name'))
    slug = AutoSlugField(max_length=70, unique=True, populate_from=get_latin_name, verbose_name='URL')
    description_short = models.TextField(verbose_name=_('description short'))
    description_long = models.TextField(verbose_name=_('description_long'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name=_('products'))
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
        ordering = ['id']

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


class Shop(models.Model):
    """
    Модель магазина
    """
    name = models.CharField(max_length=256, verbose_name=_('name'))
    slug = AutoSlugField(max_length=70, unique=True, populate_from=get_latin_name, verbose_name='URL')
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_shops')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='with_products')
    count_left = models.IntegerField(default=0, verbose_name=_('left in shop'))
    count_sold = models.IntegerField(default=0, verbose_name=_('sold in shop'))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('price'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))

    def __str__(self):
        return self.product.name


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
        ordering = ['id']

    def __str__(self):
        return f'Image of product: {self.product.name}'



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
    

class Banner(models.Model):
    """
    Модель Баннера главной страницы
    """
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='banner')
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    photo = models.ImageField(upload_to=get_banner_img_path, null=True, blank=True, verbose_name=_('image'),
                              validators=[FileExtensionValidator(['png'])])
    
    def clean(self):
        if not self.photo:
            err_text = _('No image!')
            raise ValidationError(err_text)
        else:
            w, h = get_image_dimensions(self.photo)
            if w < 250:
                raise ValidationError(f'The image is {w} pixel wide. It\'s supposed to be >= 250px')
            if h < 250:
                raise ValidationError(f'The image is {h} pixel high. It\'s supposed to be >= 250px')
    

    def __str__(self):
        return f'The banner of {self.product.name}'

    class Meta:
        verbose_name_plural = _('banners')
        verbose_name = _('banner')
        ordering = ['created']

