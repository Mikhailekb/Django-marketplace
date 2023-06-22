from modeltranslation.translator import register, TranslationOptions

from .models import DeliveryCategory, PaymentCategory


@register(DeliveryCategory)
class DeliveryCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(PaymentCategory)
class PaymentCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
