from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField(unique=True, null=True, blank=True, verbose_name=_('phone'))
    avatar = models.FileField(null=True, blank=True, upload_to="profiles/avatars/", verbose_name=_('avatar'))
    name = models.CharField(default='', max_length=100, verbose_name=_('name'))
    surname = models.CharField(default='', max_length=100, verbose_name=_('surname'))
    patronymic = models.CharField(default='', max_length=100, verbose_name=_('patronymic'))

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return self.user.username


