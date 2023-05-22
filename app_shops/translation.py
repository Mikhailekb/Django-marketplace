from modeltranslation.translator import register, TranslationOptions

from .models.category import Category
from .models.discount import Discount
from .models.product import Product, TagProduct, SortProduct, FeatureName
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


@register(Discount)
class DiscountTranslationOptions(TranslationOptions):
    fields = ('name', 'description_short', 'description_long')
