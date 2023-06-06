from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppShopsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_shops'
    verbose_name = _('marketplace')

    def ready(self):
        import app_shops.signals
        from .services import img_processors
