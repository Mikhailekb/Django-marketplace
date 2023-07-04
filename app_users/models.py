from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from imagekit.models import ProcessedImageField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django_cleanup import cleanup


def validate_name(value):
    if not (value and len(value.split()) == 3):
        raise ValidationError("Введите полное ФИО")

    for elem in value.split():
        if not elem.isalpha():
            raise ValidationError("В строке присутствуют недопустимые символы")


def get_avatar_path(instance, name):
    return f'img/content/users/{instance}/{name}'


def file_size(value):
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Размер файла не должен превышать 2 mb.')


@cleanup.select
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("user"))
    phone = PhoneNumberField(unique=True, null=True, verbose_name=_('phone'))
    avatar = ProcessedImageField(upload_to=get_avatar_path, options={'quality': 80}, validators=[file_size], null=True, blank=True, verbose_name=_("photo"))
    name = models.CharField(default='', max_length=100, validators=[validate_name], verbose_name=_('name'))

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return self.user.username
