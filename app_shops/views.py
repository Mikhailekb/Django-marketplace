from django.core.cache import cache
from django.db.models import QuerySet, Avg, Min, Max
from django.views.generic import TemplateView, ListView

from app_shops.filters import ProductFilter
from app_shops.forms import FilterGoodsForm
from app_shops.models import SortProduct, Product, TagProduct
from django_marketplace.constants import SORT_OPTIONS_CACHE_LIFETIME, PRODUCTS_CACHE_LIFETIME, TAGS_CACHE_LIFETIME


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
        self.form = FilterGoodsForm()
        self.price_from = None
        self.price_to = None
        self.ordering_to_db = None
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
        model = 'in_shops__'
        if new_ordering and new_ordering.startswith('-'):
            prefix = '-'
            new_ordering = new_ordering[1:]
        else:
            prefix = ''
        options = [option.sort_field for option in self.sort_options]
        if new_ordering in options:
            self.ordering = new_ordering
            if new_ordering == 'created':
                model = ''
        else:
            self.ordering = 'count_sold'
        self.ordering_to_db = f'{prefix}{model}{self.ordering}'
        return self.ordering_to_db

    def get_queryset(self):
        slug = self.kwargs.get('category_slug')
        self.queryset: QuerySet = cache.get_or_set(f'products_{slug}', Product.objects.filter(
                is_active=True, sellers__isnull=False, category__slug=slug).select_related('category', 'main_image'),
                                                   timeout=PRODUCTS_CACHE_LIFETIME)

        ordering = self.get_ordering()

        self.queryset = self.queryset.order_by(ordering)
        self.queryset = self.queryset.annotate(avg_price=Avg('in_shops__price'),
                                               min_price=Min('in_shops__price'),
                                               max_price=Max('in_shops__price'))

        tag = self.request.GET.get('tag')
        if tag:
            self.queryset = self.queryset.filter(tags__codename=tag)
        form = FilterGoodsForm(self.request.GET)
        if form.is_valid():
            self.form = form
            self.price_from, self.price_to = form.cleaned_data['price'].split(';')
            name = form.cleaned_data['name']
            in_stock = form.cleaned_data['in_stock']
            # free_shipping = form.cleaned_data['free_shipping']

            options = {'min_price': self.price_from, 'max_price': self.price_to,
                       'name_or_description': name, 'in_stock': in_stock}

            filter_obj = ProductFilter(options, queryset=self.queryset)
            filter_queryset = filter_obj.qs
            return filter_queryset

        return self.queryset

    def sorting_update(self):
        for item in self.sort_options:
            modulo_filed_name = None
            filed_name = item.sort_field
            if filed_name.startswith('-'):
                modulo_filed_name = filed_name[1:]

            if filed_name == self.ordering or modulo_filed_name == self.ordering:
                if self.ordering_to_db.startswith('-'):
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
        queryset = object_list if object_list is not None else self.get_queryset()
        context = super().get_context_data(object_list=queryset, **kwargs)

        min_price = self.queryset.aggregate(Min('min_price')).get('min_price__min')
        max_price = self.queryset.aggregate(Max('max_price')).get('max_price__max')
        self.sorting_update()

        if self.ordering_to_db.startswith('-'):
            self.ordering = '-' + self.ordering

        context['sort_options'] = self.sort_options
        context['tags'] = cache.get_or_set('tags', TagProduct.objects.all(), timeout=TAGS_CACHE_LIFETIME)
        context['order_by'] = self.ordering
        context['price_from'] = self.price_from if self.price_from else min_price
        context['price_to'] = self.price_to if self.price_to else max_price
        context['min_price'] = min_price
        context['max_price'] = max_price
        context['form'] = self.form
        return context
