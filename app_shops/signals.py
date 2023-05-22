from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models.category import Category
from .models.discount import Discount


@receiver([post_save, post_delete], sender=Category)
def invalidate_cache(**kwargs):
    """Удаление из кэша категории товаров, в случае изменения таблицы Category из админки"""
    cache.delete('categories')


@receiver([post_save, post_delete], sender=Discount)
def invalidate_cache(**kwargs):
    """Удаление из кэша скидок, в случае изменения таблицы Discount из админки"""
    cache.delete('sales')
