import contextlib
import os

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models.category import Category
from .models.discount import Discount
from .models.product import Product, FeatureToProduct
from .models.shop import Shop, ProductShop


@receiver([post_save, post_delete], sender=Category)
def invalidate_cache_category(**kwargs) -> None:
    """Удаление из кэша категории товаров, в случае изменения таблицы Category из админки"""
    cache.delete('categories')


@receiver([post_save, post_delete], sender=Discount)
def invalidate_cache_discount(**kwargs) -> None:
    """Удаление из кэша скидок, в случае изменения таблицы Discount из админки"""
    cache.delete('sales')


@receiver([post_save], sender=Product)
def add_recommended_features_to_product(**kwargs) -> None:
    """Добавление рекомендованных характеристик товару"""
    if not kwargs.get('created'):
        return
    instance: Product = kwargs.get('instance')
    if recommended_features := instance.category.recommended_features.all():
        objects = []
        for feature_name in recommended_features:
            if not FeatureToProduct.objects.filter(product=instance, feature_name=feature_name).exists():
                obj = FeatureToProduct(product=instance, feature_name=feature_name)
                objects.append(obj)
        if objects:
            with contextlib.suppress(IntegrityError):
                FeatureToProduct.objects.bulk_create(objects)


@receiver(post_delete)
def auto_delete_file_on_delete(sender, instance, **kwargs) -> None:
    """
    Удаление изображения с сервера, в случае его удаления из админки
    """
    if not hasattr(instance, 'image'):
        return

    image = instance.image
    if not image:
        return

    if not os.path.isfile(image.path):
        return

    os.remove(image.path)


@receiver([post_save, post_delete], sender=Shop)
def invalidate_cache_shop(**kwargs) -> None:
    """Удаление из кэша информации о магазине, в случае изменения таблицы Shop из админки"""
    slug = kwargs.get('instance').slug
    cache.delete(f'shop_{slug}')


@receiver([post_save, post_delete], sender=ProductShop)
def invalidate_cache_shop(**kwargs) -> None:
    """Удаление из кэша информации о товаре, в случае изменения таблицы ProductShop из админки"""
    instance = kwargs.get('instance')
    try:
        slug = instance.shop.slug
        cache.delete(f'products_top_{slug}')
    except ObjectDoesNotExist:
        pass

