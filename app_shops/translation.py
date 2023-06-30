from modeltranslation.translator import register, TranslationOptions

from .models.category import Category
from .models.discount import Discount
from .models.product import Product, TagProduct, FeatureName, FeatureValue
from .models.shop import Shop


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description_short', 'description_long')


@register(Shop)
class ShopTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'address')


@register(TagProduct)
class TagProductTranslationOptions(TranslationOptions):
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
