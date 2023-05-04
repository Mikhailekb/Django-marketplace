import django_filters as filters
from django.db.models import Q

from .models import ProductShop


class ProductFilter(filters.FilterSet):
    name_or_description = filters.CharFilter(method='filter_name_or_description')
    in_stock = filters.BooleanFilter(field_name='count_left', method='filter_in_stock')
    price__gte = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = filters.NumberFilter(field_name='price', lookup_expr='lte')
    # Фильтр на бесплатную доставку на данный момент отсутствует

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(count_left__gt=0)

    def filter_name_or_description(self, queryset, name, value):
        return queryset.filter(Q(product__name__icontains=value) | Q(product__description__icontains=value))

    class Meta:
        model = ProductShop
        fields = ['name_or_description', 'price__gte', 'price__lte', 'in_stock']
