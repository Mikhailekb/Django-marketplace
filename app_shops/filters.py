import django_filters as filters

from .models import ProductShop



class ProductFilter(filters.FilterSet):

    product__name = filters.CharFilter(field_name='product__name', lookup_expr='icontains')
    in_stock = filters.BooleanFilter(field_name='count_left', method='filter_in_stock')
    price__gte = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = filters.NumberFilter(field_name='price', lookup_expr='lte')
    # Фильтр на бесплатную доставку на данный момент отсутствует

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(count_left__gt=0)
    class Meta:
        model = ProductShop
        fields = ['product__name', 'price__gte', 'price__lte', 'in_stock']
