from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Case, When, DecimalField, F, QuerySet, OuterRef
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from .models.category import Category
from .models.discount import Discount, DiscountImage
from .models.product import ProductImage, Feature, Product, TagProduct, FeatureName
from .models.shop import ShopImage, ProductShop, Shop

AdminSite.site_header = 'Megano'
AdminSite.site_title = 'Megano'


class ProductImageInLine(admin.StackedInline):
    model = ProductImage


class DiscountImageInLine(admin.StackedInline):
    model = DiscountImage
    extra = 0


class DiscountInLine(admin.StackedInline):
    model = Discount
    extra = 0
    fields = (
    'name_ru', 'name_en', 'description_short_ru', 'description_short_en', 'description_long_en', 'description_long_ru',
    ('discount_amount', 'discount_percentage'), 'min_cost', 'date_start', 'date_end', 'is_active')
    show_change_link = True


class ShopImageInLine(admin.StackedInline):
    model = ShopImage
    extra = 1


class ProductShopInLine(admin.TabularInline):
    model = ProductShop
    extra = 1
    raw_id_fields = ['product', ]
    fields = ('product', 'shop', 'count_left', 'count_sold', 'price', 'discount_price', 'is_active', 'active_discount')
    readonly_fields = ('discount_price', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "active_discount":
            shop_id = request.path.split('/')[4]
            if shop_id.isdigit():
                kwargs["queryset"] = Discount.objects.filter(shop_id=shop_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def get_queryset(self, request):
        price_expression = Case(
            When(active_discount__discount_percentage__isnull=False,
                 then=F('price') - F('price') * F('active_discount__discount_percentage') / 100),
            When(active_discount__discount_amount__isnull=False,
                 then=F('price') - F('active_discount__discount_amount')),
            default=F('price'),
            output_field=DecimalField(),
        )
        qs: QuerySet = super().get_queryset(request)

        return qs.prefetch_related('product').annotate(discount_price=price_expression)

    @staticmethod
    def discount_price(obj):
        if obj.price != obj.discount_price:
            return round(obj.discount_price, 2)
        else:
            return '-'



class FeatureInLine(admin.StackedInline):
    model = Feature
    extra = 1


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ['name', 'get_icon', 'is_active', 'parent', 'slug']
    list_filter = ['is_active']
    readonly_fields = ['slug']
    list_select_related = ['parent']
    change_list_template = 'admin/categories_list.html'

    def get_icon(self, obj):
        if obj.icon:
            return mark_safe(f'<img src={obj.icon.url}>')
        else:
            return 'None'

    get_icon.short_description = _("icon")


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ['name', 'category', 'is_active']
    readonly_fields = ['slug']
    search_fields = ['name', 'description_long']
    inlines = [ProductImageInLine, ]
    filter_horizontal = ['features']
    change_list_template = "admin/product_list.html"
    save_on_top = True

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == "main_image":
            product_id = request.path.split('/')[4]
            if product_id.isdigit():
                kwargs["queryset"] = ProductImage.objects.filter(product_id=product_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Shop)
class ShopAdmin(TranslationAdmin):
    list_display = ['name', 'is_active']
    inlines = [ProductShopInLine, ShopImageInLine, DiscountInLine]
    readonly_fields = ['slug']
    save_on_top = True

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == "main_image":
            shop_id = request.path.split('/')[4]
            if shop_id.isdigit():
                kwargs["queryset"] = ShopImage.objects.filter(shop_id=shop_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Discount)
class DiscountAdmin(TranslationAdmin):
    list_display = ['name', 'is_active']
    inlines = [DiscountImageInLine, ]
    readonly_fields = ['slug', 'shop', 'get_image']
    fields = ('shop', 'name', 'description_short', 'description_long', ('discount_amount', 'discount_percentage'),
              'min_cost', 'date_start', 'date_end', 'is_active', ('main_image', 'get_image'))


    def get_image(self, obj):
        if obj.main_image:
            return mark_safe(f'<img src={obj.main_image.small.url}>')
        return ''

    get_image.short_description = ''

    def formfield_for_foreignkey(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == "main_image":
            discount_id = request.path.split('/')[4]
            if discount_id.isdigit():
                kwargs["queryset"] = DiscountImage.objects.filter(discount_id=discount_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request: HttpRequest, **kwargs):
        if db_field.name == 'goods':
            discount_id = request.path.split('/')[4]
            if discount_id.isdigit():
                discount = Discount.objects.get(id=discount_id)
                kwargs['queryset'] = ProductShop.objects.filter(shop_id=discount.shop_id)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return False


@admin.register(TagProduct)
class TagProductAdmin(TranslationAdmin):
    list_display = ['name', 'codename']
    filter_horizontal = ['goods']
    readonly_fields = ['codename']


@admin.register(FeatureName)
class FeatureAdmin(TranslationAdmin):
    inlines = [FeatureInLine]
