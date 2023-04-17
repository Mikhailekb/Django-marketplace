from django.core.cache import cache

from app_shops.models import Catalog


def get_catalog(request):
    catalog = cache.get_or_set('catalog',
                               Catalog.objects.filter(is_active=True).select_related('parent').prefetch_related(
                                   'child_category'), timeout=86400)
    return {"catalog": catalog}
