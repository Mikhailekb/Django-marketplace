import requests


def get_exchange_rate():
    data = (requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json())
    if data:
        exchange_rate = int(data['Valute']['USD']['Value'])
        return exchange_rate
