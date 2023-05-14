from django.core.cache import cache
from django.db.models import QuerySet, Avg, Min, Max, Sum
from django.views.generic import TemplateView, ListView
from django_filters.views import FilterView

from django_marketplace.constants import SORT_OPTIONS_CACHE_LIFETIME, PRODUCTS_CACHE_LIFETIME, TAGS_CACHE_LIFETIME
from .filters import ProductFilter
from .models import SortProduct, Product, TagProduct


class HomeView(TemplateView):
    """
    Представление для отображения главной страницы
    """
    template_name = 'pages/main.html'


class CatalogView(ListView):
    """
    Представление для отображения страницы каталога
    """
    template_name = 'pages/catalog.html'
    context_object_name = 'goods'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.price = None
        self.form = None
        self.sort_options: QuerySet = cache.get_or_set('sort_options', SortProduct.objects.all(),
                                                       timeout=SORT_OPTIONS_CACHE_LIFETIME)

    def get_paginate_by(self, queryset):
        self.paginate_by = 8
        if self.request.user_agent.is_mobile:
            self.paginate_by = 4
        elif self.request.user_agent.is_tablet:
            self.paginate_by = 6
        return self.paginate_by

    def get_ordering(self):
        new_ordering: str | None = self.request.GET.get('order_by')
        if new_ordering and new_ordering.startswith('-'):
            modulo_new_ordering = new_ordering[1:]
        else:
            modulo_new_ordering = new_ordering
        options = [option.sort_field for option in self.sort_options]

        if modulo_new_ordering in options:
            self.ordering = new_ordering
        else:
            self.ordering = 'count_sold'
        return self.ordering

    def get_queryset(self):
        ordering = self.get_ordering()
        filter_options = {'is_active': True, 'in_shops__is_active': True}
        category = self.request.GET.get('category')
        if category:
            filter_options['category__slug'] = category
        self.price = self.request.GET.get('price')
        annotate = {'avg_price': Avg('in_shops__price'), 'min_price': Min('in_shops__price'),
                    'max_price': Max('in_shops__price'), 'count_sold': Sum('in_shops__count_sold')}

        if self.price:
            queryset = Product.objects.filter(**filter_options).select_related('category', 'main_image').annotate(**annotate)
            filter_obj = ProductFilter(self.request.GET, queryset=queryset)
            self.form = filter_obj.form
            self.queryset = filter_obj.qs
        else:
            self.queryset = cache.get(f'products_{category}_{ordering}')

            if not self.queryset:
                queryset = Product.objects.filter(**filter_options).select_related('category', 'main_image').annotate(**annotate)
                filter_obj = ProductFilter(self.request.GET, queryset=queryset)
                self.form = filter_obj.form
                self.queryset = filter_obj.qs
                aggregate: dict = self.queryset.aggregate(min=Min('min_price'), max=Max('max_price'))
                cache.set(f'products_{category}_{ordering}', self.queryset, PRODUCTS_CACHE_LIFETIME)
                cache.set(f'aggregate_{category}', aggregate, PRODUCTS_CACHE_LIFETIME)
        return self.queryset

    def sorting_update(self):
        for item in self.sort_options:
            ordering = None
            filed_name = item.sort_field
            if self.ordering and self.ordering.startswith('-'):
                ordering = self.ordering[1:]

            if filed_name == self.ordering or filed_name == ordering:
                if self.ordering.startswith('-'):
                    item.css_class = item.css_cls[2][1]
                    item.sort_field = filed_name
                else:
                    item.css_class = item.css_cls[1][1]
                    item.sort_field = '-' + filed_name
            else:
                item.css_class = item.css_cls[0][1]
                if item.sort_field.startswith('-'):
                    item.sort_field = item.sort_field[1:]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        category = self.request.GET.get('category')
        aggregate: dict = cache.get(f'aggregate_{category}')
        if not aggregate:
            aggregate: dict = self.queryset.aggregate(min=Min('min_price'), max=Max('max_price'))
        min_price = aggregate.get('min')
        max_price = aggregate.get('max')
        self.sorting_update()

        if self.price and len(self.price.split(';')) == 2:
            price_from, price_to = self.price.split(';')
        else:
            price_from, price_to = min_price, max_price

        context['sort_options'] = self.sort_options
        context['tags'] = cache.get_or_set('tags', TagProduct.objects.all(), timeout=TAGS_CACHE_LIFETIME)
        context['order_by'] = self.ordering
        context['category'] = self.request.GET.get('category')
        context['price_from'] = price_from
        context['price_to'] = price_to
        context['min_price'] = min_price
        context['max_price'] = max_price
        context['form'] = self.form if self.form else ProductFilter().form
        return context
