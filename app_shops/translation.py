from modeltranslation.translator import register, TranslationOptions
from .models import Catalog

@register(Catalog)
class CatalogTranslationOptions(TranslationOptions):
    fields = ('name',)
