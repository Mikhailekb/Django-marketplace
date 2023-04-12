from django.core.cache import cache

from app_shops.models import Catalog


def my_context_processor(request):
    catalog = cache.get_or_set('catalog',
                               Catalog.objects.filter(is_active=True).select_related('parent').prefetch_related(
                                   'child_category'), 60 * 60 * 24)
    return {"catalog": catalog}
