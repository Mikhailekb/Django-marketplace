from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppShopsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_shops'
    verbose_name = _('marketplace')
