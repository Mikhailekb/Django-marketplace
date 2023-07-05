from __future__ import annotations

import decimal
import random

from django import template
from djmoney.money import Money

from app_shops.models.product import Product
from app_shops.services.functions import dollar_conversion

register = template.Library()


@register.filter
def localize(value, lang) -> Money | None:
    """Возвращает валюту, в зависимости от полученного языка"""
    if lang != 'ru':
        return dollar_conversion(value)

    if isinstance(value, Money):
        return value
    elif isinstance(value, (decimal.Decimal, float, int)) or (isinstance(value, str) and value.isdigit()):
        return Money(value, 'RUB')


@register.filter
def dollar_conversion_range(value, lang):
    if value:
        return int(localize(value, lang).amount)


@register.filter
def random_related_id(value: Product) -> int | None:
    if hasattr(value, 'in_shops_id'):
        return random.choice(value.in_shops_id)
