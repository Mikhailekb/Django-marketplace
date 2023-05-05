import django_filters as filters
from django.db.models import Q

from .models import Product


class ProductFilter(filters.FilterSet):
    name_or_description = filters.CharFilter(method='filter_name_or_description')
    in_stock = filters.BooleanFilter(method='filter_in_stock')
    min_price = filters.NumberFilter(method='filter_by_min_price')
    max_price = filters.NumberFilter(method='filter_by_max_price')
    # Фильтр на бесплатную доставку на данный момент отсутствует

    def filter_by_min_price(self, queryset, name, value):
        return queryset.filter(in_shops__price__gte=value)

    def filter_by_max_price(self, queryset, name, value):
        return queryset.filter(in_shops__price__lte=value)

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(in_shops__count_left__gt=0)

    def filter_name_or_description(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = Product
        fields = ['name_or_description', 'min_price', 'max_price', 'in_stock']
