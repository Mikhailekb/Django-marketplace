from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import QuerySet, Prefetch
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_admin_inline_paginator.admin import TabularInlinePaginated
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline
from django.core.cache import cache

from django_marketplace.constants import DISCOUNT_CACHE_LIFETIME
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
        'name', 'description_short', 'description_long', ('discount_amount', 'discount_percentage'),
        'min_cost', 'date_start', 'date_end', 'is_active')
    show_change_link = True


class ShopImageInLine(admin.StackedInline):
    model = ShopImage
    extra = 1


class ProductShopInLine(TabularInlinePaginated):
    model = ProductShop
    extra = 1
    raw_id_fields = ('product', )
    # autocomplete_fields = ['product']
    fields = ('product', 'count_left', 'count_sold', 'price', 'discount_price', 'discount', 'is_active')
    readonly_fields = ('discount_price',)

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        shop_id = request.path.split('/')[4]
        if shop_id.isdigit():
            if db_field.name == 'discount':
                kwargs['queryset'] = Discount.objects.filter(shop_id=shop_id, is_active=True).only('name')

                # queryset = cache.get(f'discount_{shop_id}')
                # if not queryset:
                #     print(111)
                #     queryset = Discount.objects.filter(shop_id=shop_id, is_active=True).only('name')
                #     cache.set(f'discount_{shop_id}', queryset, DISCOUNT_CACHE_LIFETIME)
                # kwargs['queryset'] = queryset

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
    list_filter = ('is_active', )
    readonly_fields = ('slug', )
    list_select_related = ('parent', )
    filter_horizontal = ('recommended_features', )
    change_list_template = 'admin/categories_list.html'

    def get_icon(self, obj):
        return mark_safe(f'<img src={obj.icon.url}>') if obj.icon else 'None'

    get_icon.short_description = _('icon')


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ('name', 'category', 'is_active')
    readonly_fields = ('slug', )
    search_fields = ('name', 'description_long')
    inlines = (ProductImageInLine, FeatureToProductInLine , ReviewInLine)
    change_list_template = 'admin/product_list.html'
    save_on_top = True

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == 'main_image':
            product_id = request.path.split('/')[4]
            if product_id.isdigit():
                kwargs['queryset'] = ProductImage.objects.filter(product_id=product_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Shop)
class ShopAdmin(TranslationAdmin):
    list_display = ('name', 'is_active')
    inlines = (ProductShopInLine, ShopImageInLine, DiscountInLine)
    # inlines = [ShopImageInLine, DiscountInLine]
    readonly_fields = ('slug', )
    save_on_top = True


    # def get_queryset(self, request: HttpRequest):
    #     qs: QuerySet = super().get_queryset(request)\
    #         .prefetch_related(
    #             Prefetch('with_products', queryset=ProductShop.objects.select_related('discount', 'product'))
    #     )
    #     # qs: QuerySet = Shop.objects.prefetch_related(
    #     #         Prefetch('with_products', queryset=ProductShop.objects.select_related('discount', 'product')))
    #
    #     return qs

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == 'main_image':
            shop_id = request.path.split('/')[4]
            if shop_id.isdigit():
                kwargs['queryset'] = ShopImage.objects.filter(shop_id=shop_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Discount)
class DiscountAdmin(TranslationAdmin):
    list_display = ('name', 'is_active')
    inlines = (DiscountImageInLine, )
    search_fields = ('name', )
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
            discount_id = request.path.split('/')[4]
            if discount_id.isdigit():
                kwargs['queryset'] = DiscountImage.objects.filter(discount_id=discount_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == 'goods':
            discount_id = request.path.split('/')[4]
            if discount_id.isdigit():
                discount = Discount.objects.get(id=discount_id)
                kwargs['queryset'] = ProductShop.objects.filter(shop_id=discount.shop_id)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def has_add_permission(self, request: HttpRequest):
        return False


@admin.register(TagProduct)
class TagProductAdmin(TranslationAdmin):
    list_display = ('name', 'codename')
    filter_horizontal = ('goods', )
    readonly_fields = ('codename', )


@admin.register(FeatureName)
class FeatureNameAdmin(TranslationAdmin):
    inlines = (FeatureValueInLine, )
