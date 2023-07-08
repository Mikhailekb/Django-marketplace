import contextlib
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_admin_inline_paginator.admin import TabularInlinePaginated
from import_export.admin import ImportExportMixin
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline
from django.core.cache import cache
from django.contrib import messages

from .models.banner import Banner, SpecialOffer, SmallBanner, SliderBanner
from .models.category import Category
from .models.discount import Discount, DiscountImage
from .models.product import ProductImage, FeatureValue, Product, TagProduct, FeatureName, FeatureToProduct, Review
from .models.shop import ShopImage, ProductShop, Shop

AdminSite.site_header = 'Megano'
AdminSite.site_title = 'Megano'


class ProductImageInLine(admin.StackedInline):
    model = ProductImage


class DiscountImageInLine(admin.StackedInline):
    model = DiscountImage
    extra = 0


class DiscountInLine(TranslationStackedInline):
    model = Discount
    extra = 0
    fields = (
        'name', 'description_short', 'description_long',
        ('discount_amount', 'discount_percentage'),
        'min_cost', 'date_start', 'date_end', 'is_active')
    show_change_link = True


class ShopImageInLine(admin.StackedInline):
    model = ShopImage
    extra = 1


class ProductShopInLine(TabularInlinePaginated):
    model = ProductShop
    extra = 1
    raw_id_fields = ('product',)
    fields = ('id', 'product', 'count_left', 'count_sold', 'price',
              'discount_price', 'discount', 'is_active')
    readonly_fields = ('id', 'discount_price',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'discount':
            with contextlib.suppress(KeyError):
                shop_id = request.path.split('/')[4]
                if shop_id.isdigit():
                    kwargs['queryset'] = Discount.objects.filter(shop_id=shop_id, is_active=True).only('name')
        elif db_field.name == 'product':
            kwargs['queryset'] = Product.objects.filter(is_active=True).only('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request: HttpRequest):
        fields = ('product__slug', 'product__description_short', 'product__description_short_ru',
                  'product__description_short_en', 'product__description_long', 'product__description_long_ru',
                  'product__description_long_en', 'product__category_id', 'product__created', 'product__updated',
                  'product__main_image_id', 'product__is_active')
        return (
            self.model.objects.with_discount_price()
            .select_related('product', ).defer(*fields)
            .order_by('id')
        )

    @staticmethod
    def discount_price(obj):
        return round(price, 2) if (price := obj.discount_price) else '-'


class FeatureValueInLine(TranslationStackedInline):
    model = FeatureValue
    extra = 1


class FeatureToProductInLine(admin.StackedInline):
    model = FeatureToProduct
    extra = 1


class ReviewInLine(admin.StackedInline):
    model = Review
    extra = 1


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('name', 'get_icon', 'is_active', 'parent', 'slug')
    list_filter = ('is_active',)
    readonly_fields = ('slug',)
    raw_id_fields = ('parent',)
    list_select_related = ('parent',)
    filter_horizontal = ('recommended_features',)
    change_list_template = 'admin/categories_list.html'

    def get_icon(self, obj):
        return mark_safe(f'<img src={obj.icon.url}>') if obj.icon else 'None'

    get_icon.short_description = _('icon')


@admin.register(Product)
class ProductAdmin(ImportExportMixin, TranslationAdmin):
    list_display = ('name', 'category', 'is_active')
    readonly_fields = ('slug',)
    search_fields = ('name', 'description_long')
    inlines = (ProductImageInLine, FeatureToProductInLine, ReviewInLine)
    import_export_change_list_template = 'admin/product_list.html'
    save_on_top = True

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == 'main_image':
            with contextlib.suppress(KeyError):
                product_id = request.path.split('/')[4]
                if product_id.isdigit():
                    kwargs['queryset'] = ProductImage.objects.filter(product_id=product_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clear_cache/', self.clear_cache, name='clear_cache'),
        ]
        return custom_urls + urls

    @staticmethod
    def clear_cache(request: HttpRequest) -> HttpResponse:
        if 'product_cache' in request.POST:
            cache.delete('tags')
            messages.success(request, _('Cache cleared successfully'))
        elif 'categories_cache' in request.POST:
            cache.delete('categories')
            messages.success(request, _('Cache cleared successfully'))
        elif 'all_cache' in request.POST:
            cache.clear()
            messages.success(request, _('Cache cleared successfully'))
        else:
            messages.warning(request, _('Error. Cache not cleared'))

        return redirect(request.META.get('HTTP_REFERER'))


@admin.register(Shop)
class ShopAdmin(TranslationAdmin):
    list_display = ('name', 'is_active')
    inlines = (ProductShopInLine, ShopImageInLine, DiscountInLine)
    readonly_fields = ('slug',)
    save_on_top = True

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == 'main_image':
            with contextlib.suppress(KeyError):
                shop_id = request.path.split('/')[4]
                if shop_id.isdigit():
                    kwargs['queryset'] = ShopImage.objects.filter(shop_id=shop_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Discount)
class DiscountAdmin(TranslationAdmin):
    list_display = ('name', 'is_active')
    inlines = (DiscountImageInLine,)
    search_fields = ('name',)
    readonly_fields = ('slug', 'shop', 'get_image')
    fields = ('shop', 'name', 'description_short', 'description_long', ('discount_amount', 'discount_percentage'),
              'min_cost', 'date_start', 'date_end', 'is_active', ('main_image', 'get_image'))

    def get_image(self, obj):
        if obj.main_image:
            return mark_safe(f'<img src={obj.main_image.small.url}>')
        return ''

    get_image.short_description = ''

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == 'main_image':
            with contextlib.suppress(KeyError):
                discount_id = request.path.split('/')[4]
                if discount_id.isdigit():
                    kwargs['queryset'] = DiscountImage.objects.filter(discount_id=discount_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @staticmethod
    def has_add_permission(*args):
        return False


@admin.register(TagProduct)
class TagProductAdmin(TranslationAdmin):
    list_display = ('name', 'codename')
    filter_horizontal = ('goods',)
    readonly_fields = ('codename',)


@admin.register(FeatureName)
class FeatureNameAdmin(TranslationAdmin):
    inlines = (FeatureValueInLine,)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('get_foreing_name', 'is_active', 'created', 'get_img')
    list_filter = ('is_active',)
    list_select_related = ('product',)

    def get_img(self, obj):
        return mark_safe(f'<img style="width: 150px; height: 150px; object-fit: contain;" src={obj.image.url}>')

    def get_foreing_name(self, obj):
        return obj.product.name

    get_img.short_description = _('image')
    get_foreing_name.short_description = _('name')


@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    raw_id_fields = ('product_shop',)

    def has_add_permission(self, request: HttpRequest):
        return not SpecialOffer.objects.exists()

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        kwargs['queryset'] = ProductShop.objects.filter(is_active=True, discount__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(SmallBanner)
class SmallBannerAdmin(admin.ModelAdmin):
    pass


@admin.register(SliderBanner)
class SmallBannerAdmin(admin.ModelAdmin):
    pass
