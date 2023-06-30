from djmoney.contrib.exchange.backends.base import BaseExchangeBackend
from djmoney.money import Money
from django.db.models import Case, When, F
from django.db.models.fields import DecimalField
import requests


class CBRExchangeBackend(BaseExchangeBackend):
    GAIN = 0.001
    name = 'cbr.ru'
    url = 'https://www.cbr-xml-daily.ru/latest.js'

    def get_rates(self, **kwargs):
        """
        Возвращает сопоставление <валюта>: <курс>.
        """
        try:
            response = requests.get(self.url).json()
            exchange_rate = response['rates']['USD'] - self.GAIN
            print('USD:', exchange_rate)
            return {'USD': exchange_rate}
        except (requests.exceptions.Timeout, requests.ConnectionError):
            return {'USD': 0.0115}


def get_prices(discounts_query):
    """
    Обрабатывает QuerySet товаров со скидками, а также считает среднюю цену товара.
    """
    shop_prices = {product_shop: {'price_old': product_shop.price.amount}
    if not product_shop.discount_price
    else {'price_old': product_shop.price.amount, 'price_new': product_shop.discount_price}
                   for product_shop in discounts_query}
    # price_list = [price.get('price_new') or price.get('price_old')
    #               for price in shop_prices.values()]
    #
    # price = float(sum([float(price) if not isinstance(price, Money) else float(price.amount)
    #                    for price in price_list]) / len(price_list))

    return shop_prices


# def refactor_discount_query(discounts_query, goods: dict):
#     """
#     Обрабатывает QuerySet товаров со скидками для получения списка цен на товары.
#     """
#     product_prices = {}
#
#     for product_shop in discounts_query:
#         price = product_shop.discount_price if product_shop.discount_price else product_shop.price.amount
#
#         if product_prices.get(product_shop.product.id):
#             product_prices[product_shop.product.id].append(price)
#         else:
#             product_prices.update({product_shop.product.id: [price, ]})
#
#     for good in goods:
#         _, price = get_prices(discounts_query, product_prices.get(good.id))
#         good.avg_price = price
#
#     return goods


price_exp = Case(
    When(in_shops__discount__is_active=False, then='in_shops__price'),
    When(in_shops__discount__discount_percentage__isnull=False,
         then=F('in_shops__price') - F('in_shops__price') *
              F('in_shops__discount__discount_percentage') / 100),

    When(in_shops__discount__discount_amount__isnull=False,
         then=F('in_shops__price') - F('in_shops__discount__discount_amount')),
    default='in_shops__price',
    output_field=DecimalField()
)

price_exp_banners = Case(
    When(product__in_shops__discount__is_active=False, then='product__in_shops__price'),
    When(product__in_shops__discount__discount_percentage__isnull=False,
         then=F('product__in_shops__price') - F('product__in_shops__price') *
              F('product__in_shops__discount__discount_percentage') / 100),

    When(product__in_shops__discount__discount_amount__isnull=False,
         then=F('product__in_shops__price') - F('product__in_shops__discount__discount_amount')),
    default='product__in_shops__price',
    output_field=DecimalField()
)


def get_object_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
