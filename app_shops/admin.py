from django.contrib import admin
from django.utils.safestring import mark_safe
from modeltranslation.admin import TranslationAdmin
from django.utils.translation import gettext_lazy as _

from app_shops.models import Category


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
