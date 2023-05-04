from django.core.cache import cache
from django.db.models import QuerySet
from django.views.generic import TemplateView, ListView

from app_shops.filters import ProductFilter
from app_shops.forms import FilterGoodsForm
from app_shops.models import ProductShop, SortProduct
from django_marketplace.constants import SORT_OPTIONS_CACHE_LIFETIME


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
        slug = self.kwargs.get('category_slug')
        self.queryset = cache.get_or_set(f'products_{slug}', ProductShop.objects.filter(is_active=True, product__category__slug=slug) \
                                         .select_related('product') \
                                         .select_related('product__category') \
                                         .select_related('product__main_image')
                                         )

        ordering = self.get_ordering()
        self.queryset = self.queryset.order_by(ordering)

        form = FilterGoodsForm(self.request.GET)
        if form.is_valid():
            self.form = form
            self.price_from, self.price_to = form.cleaned_data['price'].split(';')
            name = form.cleaned_data['name']
            in_stock = form.cleaned_data['in_stock']
            # free_shipping = form.cleaned_data['free_shipping']

            options = {'price__gte': self.price_from, 'price__lte': self.price_to,
                       'name_or_description': name, 'in_stock': in_stock}

            filter_obj = ProductFilter(options, queryset=self.queryset)
            filter_queryset = filter_obj.qs
            return filter_queryset

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
        queryset = object_list if object_list is not None else self.get_queryset()

        context = super().get_context_data(object_list=queryset, **kwargs)

        price_lst = [int(item.price) for item in self.queryset]
        min_price = min(price_lst) if price_lst else 0
        max_price = max(price_lst) if price_lst else 0
        self.sorting_update()

        context['sort_options'] = self.sort_options
        context['order_by'] = self.ordering
        context['price_from'] = self.price_from if self.price_from else min_price
        context['price_to'] = self.price_to if self.price_to else max_price
        context['min_price'] = min_price
        context['max_price'] = max_price
        context['form'] = self.form
        return context
