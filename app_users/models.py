import re
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django_cleanup import cleanup


def validate_name(value):
    if not (value and len(value.split()) == 3):
        raise ValidationError("Введите полное ФИО")

    for elem in value.split():
        if not re.match("""^[а-яА-ЯёЁ][а-яё0-9 !?:;"'.,]+$""", elem):
            raise ValidationError("В строке присутствуют недопустимые символы")


def get_avatar_path(instance, name):
    return f'img/content/users/{instance}/{name}'


def file_size(value):
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Размер файла не должен превышать 2 mb.')


@cleanup.select
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField(unique=True, null=True, blank=True, verbose_name=_('phone'))
    avatar = ProcessedImageField(upload_to=get_avatar_path, options={'quality': 80}, validators=[file_size], null=True, blank=True)
    name = models.CharField(default='', max_length=100, blank=True, validators=[validate_name], verbose_name=_('name'))
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username
