import django_filters as filters
from django.db.models import Q

from .models import Product


class ProductFilter(filters.FilterSet):
    name_or_description = filters.CharFilter(method='filter_name_or_description')
    in_stock = filters.BooleanFilter(method='filter_in_stock')
    min_price = filters.NumberFilter(method='filter_by_min_price')
    max_price = filters.NumberFilter(method='filter_by_max_price')
    # Фильтр на бесплатную доставку на данный момент отсутствует
    @staticmethod
    def filter_by_min_price(queryset, name, value):
        return queryset.filter(avg_price__gte=value)

    @staticmethod
    def filter_by_max_price(queryset, name, value):
        return queryset.filter(avg_price__lte=value)
    @staticmethod
    def filter_in_stock(queryset, name, value):
        return queryset.filter(in_shops__count_left__gt=0)

    @staticmethod
    def filter_name_or_description(queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = Product
        fields = ['name_or_description', 'min_price', 'max_price', 'in_stock']
