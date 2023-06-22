import datetime

from autoslug import AutoSlugField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from imagekit.models import ProcessedImageField, ImageSpecField


def get_discount_img_path(instance, name) -> str:
    """Возвращает путь для хранения изображений данной скидки"""
    return f'img/content/discounts/{instance.discount.slug}/{name}'


class Discount(models.Model):
    """
    Модель скидки на товары
    """
    name = models.CharField(max_length=100, verbose_name=_('title'))
    description_short = models.CharField(max_length=100, verbose_name=_('description short'))
    description_long = models.TextField(verbose_name=_('description long'))
    slug = AutoSlugField(max_length=70, unique=True, populate_from='name_en', verbose_name='URL')
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='discounts',
                             verbose_name=_('shop'))
    discount_amount = MoneyField(max_digits=8, decimal_places=2, null=True, blank=True,
                                 default_currency='RUB', verbose_name=_('discount value'))
    discount_percentage = models.PositiveSmallIntegerField(null=True, blank=True,
        validators=[MaxValueValidator(99)], verbose_name=_('discount percentage'))
    min_cost = MoneyField(max_digits=8, decimal_places=2, null=True, blank=True,
                          default_currency='RUB', verbose_name=_('minimum cost'))
    date_start = models.DateTimeField(db_index=True, verbose_name=_('date start'))
    date_end = models.DateTimeField(null=True, blank=True, verbose_name=_('date end'))
    is_active = models.BooleanField(default=True, verbose_name=_('is active'))
    main_image = models.OneToOneField('DiscountImage', related_name='main_for_discount', on_delete=models.SET_NULL,
                                      null=True, blank=True, verbose_name=_('main image'))

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name_plural = _('discounts')
        verbose_name = _('discount')
        ordering = ['-date_start']

    def clean(self):
        if not self.discount_amount and not self.discount_percentage or \
                self.discount_amount and self.discount_percentage:
            raise ValidationError(
                _('"discount value" and "discount percentage" fields cannot be used at the same time'))

        if not self.pk and self.date_start < timezone.now():
            raise ValidationError({'date_start': _('Date cannot be in the past')})
        elif self.pk:
            old_date_start = Discount.objects.get(pk=self.pk).date_start
            if self.date_start != old_date_start and self.date_start < timezone.now():
                raise ValidationError({'date_start': _('Date cannot be in the past')})

        if self.date_end and self.date_end < self.date_start:
            raise ValidationError({'date_end': _('Date end cannot be before date start')})

    def get_absolute_url(self) -> str:
        return reverse('discount', kwargs={'promo_slug': self.slug})

    @property
    def day_start(self) -> str:
        return datetime.date.strftime(self.date_start, '%d')

    @property
    def month_start(self) -> str:
        return datetime.date.strftime(self.date_start, '%b')

    @property
    def day_end(self) -> str:
        return datetime.date.strftime(self.date_end, '%d') if self.date_end else None

    @property
    def month_end(self) -> str:
        return datetime.date.strftime(self.date_end, '%b') if self.date_end else None


class DiscountImage(models.Model):
    """
    Модель изображения для скидки
    """
    image = ProcessedImageField(upload_to=get_discount_img_path, options={'quality': 80}, verbose_name=_('image'))
    small = ImageSpecField(source='image', id='app_shops:thumbnail_200x200')
    middle = ImageSpecField(source='image', id='app_shops:thumbnail_500x500')
    large = ImageSpecField(source='image', id='app_shops:thumbnail_800x800')
    discount = models.ForeignKey(
        Discount, on_delete=models.CASCADE, related_name='images', verbose_name=_('discount'))
    uploaded = models.DateTimeField(auto_now_add=True, verbose_name=_('uploaded'))

    def __str__(self) -> str:
        return f'Image of discount: {self.discount.name}'

    class Meta:
        verbose_name_plural = _('discount images')
        verbose_name = _('discount image')
