from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Catalog

@receiver([post_save, post_delete], sender=Catalog)
def invalidate_cache(**kwargs):
    """Удаление из кэша каталога товаров, в случае изменения таблицы из админки"""
    cache.delete('catalog')