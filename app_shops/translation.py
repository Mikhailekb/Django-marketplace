from modeltranslation.translator import register, TranslationOptions

from .models import Category, Product, TagProduct, Shop, SortProduct, Feature, FeatureName


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

