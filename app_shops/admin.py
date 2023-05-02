from django.contrib import admin
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from app_shops.models import Category, Product, Shop, ProductShop, ProductImage, ShopImage, SortProduct


class ProductImageInLine(admin.StackedInline):
    model = ProductImage


class ShopImageInLine(admin.StackedInline):
    model = ShopImage
    extra = 1


class ProductShopInLine(admin.StackedInline):
    model = ProductShop
    extra = 1


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ['name', 'get_icon', 'is_active', 'parent', 'slug']
    list_filter = ['is_active']

    def get_icon(self, obj):
        if obj.icon:
            return mark_safe(f'<img src={obj.icon.url}>')
        else:
            return 'None'

    get_icon.short_description = _("icon")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    inlines = [ProductImageInLine, ]

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == "main_image":
            product_id = request.path.split('/')[4]
            kwargs["queryset"] = ProductImage.objects.filter(product_id=product_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    inlines = [ProductShopInLine, ShopImageInLine]

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == "main_image":
            shop_id = request.path.split('/')[4]
            kwargs["queryset"] = ShopImage.objects.filter(shop_id=shop_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
