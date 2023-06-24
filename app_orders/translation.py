from modeltranslation.translator import register, TranslationOptions

from .models import DeliveryCategory


@register(DeliveryCategory)
class DeliveryCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
