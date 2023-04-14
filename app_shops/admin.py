from django.contrib import admin
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from modeltranslation.admin import TranslationAdmin
from django.utils.translation import gettext_lazy as _

from app_shops.models import Catalog


@admin.register(Catalog)
class CatalogAdmin(TranslationAdmin):
    list_display = ['name', 'get_icon', 'is_active', 'parent', 'slug']
    list_filter = ['is_active']

    def get_icon(self, obj):
        if obj.icon:
            return mark_safe(f'<img src={obj.icon.url}>')
        else:
            return 'None'

    get_icon.short_description = _("icon")


@receiver([post_save, post_delete], sender=Catalog)
def invalidate_cache(**kwargs):
    """Удаление из кэша каталога товаров, в случае изменения таблицы из админки"""
    cache.delete('catalog')