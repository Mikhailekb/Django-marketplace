from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions



def get_banner_img_path(instance, name):
    return f'img/content/banners/{instance.product.slug}/{name}'


class Banner(models.Model):
    """
    Модель Баннера главной страницы
    """
    product = models.OneToOneField('Product', on_delete=models.CASCADE, related_name='banner')
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

