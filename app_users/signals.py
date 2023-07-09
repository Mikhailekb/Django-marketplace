from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Создаёт Profile пользователя, после создания User"""
    if created:
        Profile.objects.create(
            user=instance,
        )


@receiver(m2m_changed, sender=Group.user_set.through)
def add_admin_status(sender, instance, action, **kwargs):
    if action == 'post_add':
        instance.is_staff = True
    else:
        instance.is_staff = False
    instance.save()




