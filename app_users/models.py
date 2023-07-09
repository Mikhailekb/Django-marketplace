from django.apps import apps
from django.contrib.auth.models import User, Permission, Group
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from imagekit.models import ProcessedImageField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django_cleanup import cleanup


@receiver(post_migrate, sender=apps.get_app_config('app_users'))
def add_admin_group(sender, **kwargs):
    admin_group, created = Group.objects.get_or_create(name=_('admins'))
    seller_group, created = Group.objects.get_or_create(name=_('sellers'))

    admin_group.permissions.set(Permission.objects.all())

    seller_group.permissions.set(Permission.objects.filter(
        Q(name__endswith='discount') | Q(name__endswith='image') |
        Q(name__endswith='product') | Q(name__endswith='value') | Q(name__endswith='category') |
        Q(name__endswith='payment_item') | Q(name__endswith='image') | Q(name__endswith='shop') |
        Q(name__endswith='offer')
    ))

    admin_group.save()

    seller_group.save()


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
