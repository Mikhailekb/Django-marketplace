from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import QuerySet, Avg, Min, Max, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django_filters.views import FilterView

from django_marketplace.constants import SORT_OPTIONS_CACHE_LIFETIME, TAGS_CACHE_LIFETIME, SALES_CACHE_LIFETIME
from .filters import ProductFilter
from .models.discount import Discount
from .models.product import SortProduct, Product, TagProduct
from .models.shop import ProductShop


class HomeView(TemplateView):
    """
    Представление для отображения главной страницы
    """
    template_name = 'pages/main.html'


class CatalogView(FilterView):
    """
    Представление для отображения страницы каталога
    """
    template_name = 'pages/catalog.html'
    context_object_name = 'goods'
    filterset_class = ProductFilter

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sort_options: QuerySet = cache.get_or_set('sort_options', SortProduct.objects.all(),
                                                       timeout=SORT_OPTIONS_CACHE_LIFETIME)

    def get_paginate_by(self, queryset):
        self.paginate_by = 8
        if self.request.user_agent.is_mobile:
            self.paginate_by = 4
        elif self.request.user_agent.is_tablet:
            self.paginate_by = 6
        return self.paginate_by

    def get_queryset(self):
        filter_options = {'is_active': True, 'in_shops__is_active': True}
        if category := self.request.GET.get('category'):
            filter_options['category__slug'] = category
        self.queryset = Product.objects.filter(**filter_options) \
            .select_related('category', 'main_image') \
            .annotate(avg_price=Avg('in_shops__price'),
                      min_price=Min('in_shops__price'),
                      max_price=Max('in_shops__price'),
                      count_sold=Sum('in_shops__count_sold'))
        return self.queryset

    def sorting_update(self):
        for item in self.sort_options:
            ordering = None
            filed_name = item.sort_field
            if self.ordering and self.ordering.startswith('-'):
                ordering = self.ordering[1:]

            if filed_name in [self.ordering, ordering]:
                if self.ordering.startswith('-'):
                    item.css_class = item.css_cls[2][1]
                    item.sort_field = filed_name
                else:
                    item.css_class = item.css_cls[1][1]
                    item.sort_field = f'-{filed_name}'
            else:
                item.css_class = item.css_cls[0][1]
                if item.sort_field.startswith('-'):
                    item.sort_field = item.sort_field[1:]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        aggregate: dict = self.queryset.aggregate(min=Min('min_price'), max=Max('max_price'))
        min_price = aggregate.get('min')
        max_price = aggregate.get('max')

        self.ordering = self.filterset.data.get('order_by') or 'count_sold'
        self.sorting_update()

        price = self.filterset.data.get('price')
        if price and len(price.split(';')) == 2 and all(item.isdigit() for item in price.split(';')):
            price_from, price_to = price.split(';')
        else:
            price_from, price_to = min_price, max_price

        category = self.request.GET.get('category')

        context['sort_options'] = self.sort_options
        context['tags'] = cache.get_or_set('tags', TagProduct.objects.all(), timeout=TAGS_CACHE_LIFETIME)
        context['order_by'] = self.ordering
        context['category'] = category or ''
        context['price_from'] = price_from
        context['price_to'] = price_to
        context['min_price'] = min_price
        context['max_price'] = max_price
        context['form'] = self.filterset.form
        return context


class SaleView(ListView):
    """
    Представление для отображения страницы списка распродаж
    """
    template_name = 'pages/sale.html'
    context_object_name = 'sales'

    def get_queryset(self):
        self.queryset = cache.get_or_set('sales', Discount.objects.filter(is_active=True,
                                                                          date_start__lte=timezone.now()) \
                                         .select_related('main_image'),
                                         timeout=SALES_CACHE_LIFETIME)
        return self.queryset

    def get_paginate_by(self, queryset):
        self.paginate_by = 12
        if self.request.user_agent.is_tablet:
            self.paginate_by = 10
        elif self.request.user_agent.is_mobile:
            self.paginate_by = 8
        return self.paginate_by


class DiscountDetailView(DetailView):
    model = Discount
    template_name = 'pages/discount.html'
    context_object_name = 'discount'
    slug_url_kwarg = 'discount_slug'

    def get(self, request, *args, **kwargs):
        self.object: Discount = self.get_object()
        if not self.object.is_active or self.object.date_start > timezone.now():
            return redirect('sales')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj: Discount = kwargs.get('object')
        goods = ProductShop.objects \
            .with_discount_price() \
            .filter(discount=obj) \
            .select_related('product__main_image', 'product__category') \
            .order_by('product__name')
        if date_end := obj.date_end:
            context['date_end'] = date_end.strftime('%d.%m.%Y %H:%M')

        paginate_by = 8
        if self.request.user_agent.is_mobile:
            paginate_by = 4
        elif self.request.user_agent.is_tablet:
            paginate_by = 6

        paginator = Paginator(goods, paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


class ClearCache(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_staff:
            raise PermissionError

        if 'product_cache' in request.POST:
            cache.delete('sort_options')
            cache.delete('tags')
            messages.success(self.request, _('Cache cleared successfully'))
        elif 'categories_cache' in request.POST:
            cache.delete('categories')
            messages.success(self.request, _('Cache cleared successfully'))
        elif 'all_cache' in request.POST:
            cache.clear()
            messages.success(self.request, _('Cache cleared successfully'))
        else:
            messages.warning(self.request, _('Error. Cache not cleared'))

        return redirect(request.META.get('HTTP_REFERER'))
