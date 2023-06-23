from djmoney.contrib.exchange.backends.base import BaseExchangeBackend
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


def get_object_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
