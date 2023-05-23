from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from autoslug import AutoSlugField
from django.core.validators import FileExtensionValidator


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