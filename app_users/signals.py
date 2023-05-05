from django.contrib.auth.models import User
from django.db.backends.signals import connection_created
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Создаёт Profile пользователя, после создания User"""
    if created:
        Profile.objects.create(
            user=instance
        )






