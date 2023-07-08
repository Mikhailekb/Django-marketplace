from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions


def get_banner_img_path(instance, name) -> str:
    """Возвращает путь для хранения изображений банера"""
    return f'img/content/banners/{instance.product.slug}/{name}'


def get_small_banner_img_path(instance, name) -> str:
    """Возвращает путь для хранения изображений маленького банера"""
    return f'img/content/small_banners/{instance.product.slug}/{name}'


class Banner(models.Model):
    """
    Модель Баннера главной страницы
    """
    product = models.OneToOneField('Product', on_delete=models.CASCADE, related_name='banner')
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    image = models.ImageField(upload_to=get_banner_img_path, null=True, blank=True,
                              validators=[FileExtensionValidator(['png'])], verbose_name=_('image'))

    def __str__(self):
        return f'The banner of {self.product.name}'

    class Meta:
        verbose_name_plural = _('banners')
        verbose_name = _('banner')
        ordering = ('created',)

    def clean(self):
        w, h = get_image_dimensions(self.image)
        if w < 250:
            raise ValidationError(f'The image is {w} pixel wide. It\'s supposed to be >= 250px')
        if h < 250:
            raise ValidationError(f'The image is {h} pixel high. It\'s supposed to be >= 250px')


class SpecialOffer(models.Model):
    """
    Модель специального предложения на главной страницы
    """
    product_shop = models.ForeignKey('ProductShop', on_delete=models.CASCADE, verbose_name=_('product shop'))
    date_end = models.DateTimeField(null=True, blank=True, verbose_name=_('date end'))

    def __str__(self):
        return self.product_shop.product.name

    class Meta:
        verbose_name_plural = _('special offer')
        verbose_name = _('special offer')

    def clean(self):
        # Может быть только 1 экземпляр
        if not self.pk and SpecialOffer.objects.exists():
            raise ValidationError(_('Only one instance of this model is allowed.'))


class SmallBanner(models.Model):
    """
    Модель маленького баннера на главной страницы
    """
    product = models.ForeignKey('Product', null=True, on_delete=models.CASCADE,
                                related_name='in_small_banner', verbose_name=_('product'))
    image = models.ImageField(upload_to=get_small_banner_img_path, null=True, blank=True,
                              validators=[FileExtensionValidator(['png'])], verbose_name=_('image'))

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = _('small banners')
        verbose_name = _('small banner')

    def clean(self):
        # Может быть только 3 экземпляра
        if SmallBanner.objects.count() >= 3 and not self.pk:
            raise ValidationError(_('The maximum number of items (3 items) has been reached'))


class SliderBanner(models.Model):
    """
    Модель маленького баннера на главной страницы
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE,
                                related_name='in_slider_banner', verbose_name=_('product'))

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = _('slider banners')
        verbose_name = _('slider banner')

    def clean(self):
        # Может быть только 10 экземпляров
        if SliderBanner.objects.count() >= 10 and not self.pk:
            raise ValidationError(_('The maximum number of items (10 items) has been reached'))
