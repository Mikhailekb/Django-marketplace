import django_filters as filters
from django.db.models import Q
from django import forms

from .models import Product


class ProductFilter(filters.FilterSet):
    order_by = filters.OrderingFilter(fields=('count_sold', 'avg_price', 'created'))

    price = filters.CharFilter(method='filter_price')
    name = filters.CharFilter(method='filter_name_or_description')
    in_stock = filters.BooleanFilter(method='filter_in_stock', widget=forms.CheckboxInput)
    tag = filters.CharFilter(field_name='tags__codename')
    # Фильтр на бесплатную доставку на данный момент отсутствует

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if data:
            if not data.get('order_by'):
                data = data.dict()
                data['order_by'] = 'count_sold'
        super().__init__(data, queryset, request=request, prefix=prefix)


    @staticmethod
    def filter_price(queryset, name, value):
        if len(value.split(';')) == 2:
            price_from, price_to = value.split(';')
            return queryset.filter(avg_price__gte=price_from, avg_price__lte=price_to)
        return queryset

    @staticmethod
    def filter_name_or_description(queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))

    @staticmethod
    def filter_in_stock(queryset, name, value):
        return queryset.filter(in_shops__count_left__gt=0)



    class Meta:
        model = Product
        fields = ['price', 'name', 'in_stock']


