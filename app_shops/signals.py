import contextlib
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models.category import Category
from .models.discount import Discount
from .models.product import Product, FeatureToProduct


@receiver([post_save, post_delete], sender=Category)
def invalidate_cache_category(**kwargs):
    """Удаление из кэша категории товаров, в случае изменения таблицы Category из админки"""
    cache.delete('categories')


@receiver([post_save, post_delete], sender=Discount)
def invalidate_cache_discount(**kwargs):
    """Удаление из кэша скидок, в случае изменения таблицы Discount из админки"""
    cache.delete('sales')


@receiver([post_save], sender=Product)
def add_recommended_features_to_product(**kwargs):
    """Добавление рекомендованных характеристик товару"""
    if not kwargs.get('created'):
        return
    instance: Product = kwargs.get('instance')
    recommended_features = instance.category.recommended_features.all()
    if recommended_features.exists():
        objects = []
        for feature in recommended_features:
            if not FeatureToProduct.objects.filter(product=instance, feature_name=feature).exists():
                obj = FeatureToProduct(product=instance, feature_name=feature)
                objects.append(obj)
        if objects:
            with contextlib.suppress(IntegrityError):
                FeatureToProduct.objects.bulk_create(objects)
