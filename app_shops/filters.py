import django_filters as filters
from django import forms
from django.db.models import Q
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money

from django_marketplace.constants import ORDER_AMOUNT_WHICH_DELIVERY_FREE
from .models.product import Product


class ProductFilter(filters.FilterSet):
    order_by = filters.OrderingFilter(
        fields=('count_sold', 'avg_price', 'created', 'feedback'))

    price = filters.CharFilter(method='filter_price')
    name = filters.CharFilter(method='filter_name_or_description')
    in_stock = filters.BooleanFilter(method='filter_in_stock', widget=forms.CheckboxInput)
    free_delivery = filters.BooleanFilter(method='filter_free_delivery', widget=forms.CheckboxInput)
    tag = filters.CharFilter(field_name='tags__codename')

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if data:
            data = data.dict()
            if price := data.get('price'):
                data['price'] = f'{price};{request.LANGUAGE_CODE}'
        super().__init__(data, queryset, request=request, prefix=prefix)

    @staticmethod
    def filter_price(queryset, name, value):
        if len(value.split(';')) == 3:
            price_from, price_to, language_code = value.split(';')
            if price_from.isdigit() and price_to.isdigit():
                if language_code == 'en':
                    price_from = convert_money(
                        Money(price_from, 'USD'), 'RUB').amount
                    price_to = convert_money(
                        Money(price_to, 'USD'), 'RUB').amount
                return queryset.filter(avg_price__gte=price_from, avg_price__lte=price_to)
        return queryset

    @staticmethod
    def filter_name_or_description(queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(description_long__icontains=value))

    @staticmethod
    def filter_in_stock(queryset, name, value):
        return queryset.filter(in_shops__count_left__gt=0) if value else queryset

    @staticmethod
    def filter_free_delivery(queryset, name, value):
        return queryset.filter(min_price__gte=ORDER_AMOUNT_WHICH_DELIVERY_FREE) if value else queryset

    class Meta:
        model = Product
        fields = ['price', 'name', 'in_stock', 'free_delivery']
