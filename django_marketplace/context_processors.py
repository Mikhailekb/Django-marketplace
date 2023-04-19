from django.core.cache import cache

from app_shops.models import Category
from django_marketplace.constants import CATEGORIES_CACHE_LIFETIME


def get_catalog(request):
    categories = cache.get_or_set('categories',
                               Category.objects.filter(is_active=True).select_related('parent').prefetch_related(
                                   'child_category'), timeout=CATEGORIES_CACHE_LIFETIME)
    return {"categories": categories}
