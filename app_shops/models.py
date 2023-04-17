from autoslug import AutoSlugField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from uuslug import slugify


def get_latin_name(instance):
    return slugify(instance.name)


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