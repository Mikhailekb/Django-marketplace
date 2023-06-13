from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Создаёт Profile пользователя, после создания User"""
    if created:
        Profile.objects.create(
            user=instance,
            name=instance.username
        )


# @receiver(connection_created)
# def create_groups(sender, connection, **kwargs):
#     admin_group = Group.objects.get_or_create(name=_('admins'))
#
#     creator_group = Group.objects.get_or_create(name=_('creators'))



