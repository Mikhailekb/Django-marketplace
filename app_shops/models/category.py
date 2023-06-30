from autoslug import AutoSlugField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Модель категории товаров
    """
    name = models.CharField(max_length=100, verbose_name=_('name'))
    slug = AutoSlugField(max_length=70, unique=True, populate_from='name_en', verbose_name='URL')
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='child_category', verbose_name=_('parent category'))
    icon = models.FileField(upload_to='img/icons/departments/', null=True, blank=True,
                            validators=[FileExtensionValidator(['svg'])], verbose_name=_('icon'))
    recommended_features = models.ManyToManyField('FeatureName', related_name='categories',
                                                  blank=True, verbose_name=_('recommended features'))

    def __str__(self) -> str:
        return f'{self.name} ({self.parent})' if self.parent else self.name

    class Meta:
        verbose_name_plural = _('categories')
        verbose_name = _('category')
        ordering = ['name']

    def get_absolute_url(self) -> str:
        catalog_url = reverse('catalog')
        return f'{catalog_url}?category={self.slug}'
