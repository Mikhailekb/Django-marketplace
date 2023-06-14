from modeltranslation.translator import register, TranslationOptions

from .models.category import Category
from .models.discount import Discount
from .models.order import PaymentCategory, DeliveryCategory
from .models.product import Product, TagProduct, SortProduct, FeatureName, FeatureValue
from .models.shop import Shop


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Product)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description_short', 'description_long')


@register(Shop)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'address')


@register(TagProduct)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(SortProduct)
class SortProductTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(FeatureName)
class FeatureNameTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(FeatureValue)
class FeatureValueTranslationOptions(TranslationOptions):
    fields = ('value',)


@register(Discount)
class DiscountTranslationOptions(TranslationOptions):
    fields = ('name', 'description_short', 'description_long')


@register(DeliveryCategory)
class DeliveryCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(PaymentCategory)
class PaymentCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
