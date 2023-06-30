from __future__ import annotations

import decimal

from django import template
from djmoney.money import Money

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
    return int(localize(value, lang).amount)
