from django.core.cache import cache

from app_shops.models import Catalog
from django_marketplace.constants import CATALOG_CACHE_LIFETIME


def get_catalog(request):
    catalog = cache.get_or_set('catalog',
                               Catalog.objects.filter(is_active=True).select_related('parent').prefetch_related(
                                   'child_category'), timeout=CATALOG_CACHE_LIFETIME)
    return {"catalog": catalog}
