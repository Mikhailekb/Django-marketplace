from typing import Dict

from django.core.cache import cache
from django.http import HttpRequest

from app_shops.models.category import Category
from django_marketplace.constants import CATEGORIES_CACHE_LIFETIME

from app_cart.cart import Cart


def get_categories(request: HttpRequest) -> Dict:
    categories = cache.get_or_set('categories',
                                  Category.objects.filter(is_active=True).select_related('parent').prefetch_related(
                                      'child_category'), timeout=CATEGORIES_CACHE_LIFETIME)
    query_params = request.GET.copy()
    query_params.pop('price', None)
    redirect_to = f'{request.path}?{query_params.urlencode()}'
    return {"categories": categories, 'redirect_to': redirect_to}


def get_cart(request):
    return {'cart': Cart(request)}
