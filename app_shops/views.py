from django.core.cache import cache
from django.db.models import QuerySet, Avg, Min, Max, Subquery, OuterRef, Sum
from django.views.generic import TemplateView, ListView

from .filters import ProductFilter
from .forms import FilterGoodsForm
from .models import SortProduct, Product, TagProduct
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
        slug = self.kwargs.get('category_slug')
        self.queryset: QuerySet = cache.get_or_set(key=f'products_{slug}_{ordering}', timeout=PRODUCTS_CACHE_LIFETIME,
                    default=Product.objects.filter(is_active=True, in_shops__is_active=True, category__slug=slug)\
                                           .select_related('category', 'main_image')\
                                           .annotate(avg_price=Avg('in_shops__price'),
                                                     min_price=Min('in_shops__price'),
                                                     max_price=Max('in_shops__price'),
                                                     count_sold=Sum('in_shops__count_sold')).order_by(ordering))

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

        aggregate = self.queryset.aggregate(min=Min('min_price'), max=Max('max_price'))
        min_price = aggregate.get('min')
        max_price = aggregate.get('max')
        self.sorting_update()

        context['sort_options'] = self.sort_options
        context['tags'] = cache.get_or_set('tags', TagProduct.objects.all(), timeout=TAGS_CACHE_LIFETIME)
        context['order_by'] = self.ordering
        context['price_from'] = self.price_from if self.price_from else min_price
        context['price_to'] = self.price_to if self.price_to else max_price
        context['min_price'] = min_price
        context['max_price'] = max_price
        context['form'] = self.form
        return context
