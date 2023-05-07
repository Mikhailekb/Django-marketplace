from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Category, ProductShop


@receiver([post_save, post_delete], sender=Category)
def invalidate_cache(**kwargs):
    """Удаление из кэша категории товаров, в случае изменения таблицы Category из админки"""
    cache.delete('categories')


@receiver([post_save, post_delete], sender=ProductShop)
def invalidate_cache(**kwargs):
    """
    Удаление из кэша каталога товаров определённой категории,
    в случае изменения таблицы ProductShop из админки
     """
    instance: ProductShop = kwargs.get('instance')
    slug = instance.product.category.slug
    sort_options = cache.get('sort_options')
    options = [option.sort_field for option in sort_options]
    for option in options:
        cache.delete(f'products_{slug}_{option}')
        cache.delete(f'products_{slug}_-{option}')
