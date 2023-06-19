from __future__ import annotations

import decimal

from django import template
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money

register = template.Library()


@register.filter
def dollar_conversion(value) -> Money | None:
    """Конвертация рублей в доллары"""
    if isinstance(value, Money):
        return convert_money(value, 'USD')
    elif isinstance(value, (decimal.Decimal, float, int)):
        return convert_money(Money(value, 'RUB'), 'USD')
    elif isinstance(value, str) and value.isdigit():
        return convert_money(Money(value, 'RUB'), 'USD')


@register.filter
def dollar_conversion_range(value):
    return int(dollar_conversion(value).amount)
