from django.contrib import admin
from django_admin_inline_paginator.admin import TabularInlinePaginated
from modeltranslation.admin import TranslationAdmin

from app_orders.models import PaymentItem, OrderItem, Order, DeliveryCategory


class OrderItemInLine(TabularInlinePaginated):
    model = OrderItem
    extra = 0
    ordering = ('id',)
    readonly_fields = ('product_shop', 'price_on_add_moment', 'quantity')

    def get_queryset(self, request):
        try:
            order_id = request.path.split('/')[4]
            return OrderItem.objects.filter(order_id=order_id).select_related('product_shop', 'product_shop__product') \
                .only('order_id', 'product_shop__product__name_ru', 'product_shop__product__name_en',
                      'price_on_add_moment', 'price_on_add_moment_currency', 'quantity')
        except KeyError:
            return super().get_queryset(request)

    @staticmethod
    def has_add_permission(*args):
        return False

    @staticmethod
    def has_delete_permission(*args):
        return False


class PaymentItemInLine(admin.StackedInline):
    model = PaymentItem
    readonly_fields = ('is_passed', 'payment_category',
                       'total_price', 'from_account')

    @staticmethod
    def has_delete_permission(*args):
        return False


@admin.register(DeliveryCategory)
class DeliveryCategoryAdmin(TranslationAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ('buyer', 'status', 'comment', 'delivery_category', 'is_free_delivery', 'name', 'phone',
              'email', 'city', 'address', 'is_canceled', 'created', 'updated')
    readonly_fields = ('buyer', 'created', 'updated', 'is_free_delivery', 'delivery_category', 'status',)
    inlines = (PaymentItemInLine, OrderItemInLine)
    list_display = ('__str__', 'created')
    search_fields = ('id', 'phone', 'email', 'address')

    @staticmethod
    def has_delete_permission(*args):
        return False

    @staticmethod
    def has_add_permission(*args):
        return False
