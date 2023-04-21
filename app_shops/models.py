from autoslug import AutoSlugField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from uuslug import slugify
from phonenumber_field.modelfields import PhoneNumberField


def get_latin_name(instance):
    return slugify(instance.name)


def get_good_img_path(instance):
    return f'static/img/content/home/products/{instance.slug}/'


def get_shop_img_path(instance):
    return f'static/img/content/home/shops/{instance.slug}/'


class Catalog(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    slug = AutoSlugField('URL', max_length=70, unique=True, populate_from=get_latin_name)
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    parent = models.ForeignKey('Catalog', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='child_category', verbose_name=_('parent category'))
    icon = models.FileField(upload_to='static/img/icons/departments/', null=True, blank=True, verbose_name=_('icon'),
                              validators=[FileExtensionValidator(['svg'])])

    class Meta:
        verbose_name_plural = _('catalog')
        verbose_name = _('category')

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
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', verbose_name=_('products'))

    # По этому полю предлагаю определять, попадет ли товар в БАННЕРЫ
    img_big = models.FileField(upload_to=get_good_img_path, null=True, blank=True, verbose_name=_('banner img'),
                            validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    img_small = models.FileField(upload_to=get_good_img_path, null=True, blank=True, verbose_name=_('small img'),
                               validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])

    salers = models.ManyToManyField('Shop', through='ProductShop')

    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))

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

    logo_small = models.FileField(upload_to=get_good_img_path, null=True, blank=True, verbose_name=_('small logo'),
                                 validators=[FileExtensionValidator(['png', 'svg'])])
    logo_big = models.FileField(upload_to=get_good_img_path, null=True, blank=True, verbose_name=_('big logo'),
                                  validators=[FileExtensionValidator(['png', 'svg'])])
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('is active'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('edited'))

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


