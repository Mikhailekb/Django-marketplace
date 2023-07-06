from __future__ import annotations

import random
from decimal import Decimal
from typing import Union

from django import template
from django.utils.translation import gettext_lazy as _
from djmoney.money import Money

from app_shops.models.product import Product
from app_shops.services.functions import conversion_to_dollar

register = template.Library()


@register.filter
def localize(value, lang) -> Money:
    """Возвращает валюту, в зависимости от полученного языка"""
    if lang != 'ru':
        return conversion_to_dollar(value)

    if isinstance(value, Money):
        return value
    elif isinstance(value, (Decimal, float, int)) or (isinstance(value, str) and value.isdigit()):
        return Money(value, 'RUB')
    else:
        value_type = type(value)
        raise ValueError(_(f'Number expected, received {value_type}'))


@register.filter
def dollar_conversion_range(value, lang) -> Union[int, None]:
    if value:
        return int(localize(value, lang).amount)


@register.filter
def random_related_id(value: Product) -> int:
    if hasattr(value, 'in_shops_id'):
        return random.choice(value.in_shops_id)
    else:
        raise ValueError(_('The received argument does not have the "in_shops_id" attribute'))
