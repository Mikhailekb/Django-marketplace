from django.conf import settings
from djmoney.money import Money

from app_shops.models.shop import ProductShop
from app_shops.services.functions import conversion_to_dollar


class Cart:

    def __init__(self, request):
        """Инициализация объекта корзины."""
        self.request = request
        self.session = request.session
        session_cart = self.session.get(settings.CART_SESSION_ID)
        if not session_cart:
            session_cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = session_cart

    def add(self, product_shop, quantity=1, update_quantity=False):
        """
        Добавить продукт в корзину или обновить его количество.
        """
        product_shop_id = str(product_shop.id)
        if product_shop_id not in self.cart:
            if product_shop.discount_price:
                price = float(round(product_shop.discount_price, 2))
            else:
                price = float(product_shop.price.amount)
            self.cart[product_shop_id] = {'quantity': 0, 'price': price}
        if update_quantity:
            self.cart[product_shop_id]['quantity'] = quantity
        else:
            self.cart[product_shop_id]['quantity'] += quantity
        self.save()

    def minus(self, product_shop):
        """
        Удалить один экземпляр продукта из корзины
        """
        product_shop_id = str(product_shop.id)
        if product_shop_id in self.cart:
            self.cart[product_shop_id]['quantity'] -= 1
            self.save()
        if self.cart[product_shop_id]['quantity'] < 1:
            self.remove(product_shop_id)

    def save(self):
        """Обновление сессии cart"""
        self.session[settings.CART_SESSION_ID] = self.cart

    def remove(self, product_shop_id):
        """
        Удаление товара из корзины.
        """
        product_shop_id = str(product_shop_id)
        if product_shop_id in self.cart:
            del self.cart[product_shop_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = ProductShop.objects.filter(id__in=product_ids) \
            .select_related('product', 'shop', 'product__main_image')

        goods = {
            product_shop_id: {
                'price': cart_item['price'],
                'quantity': cart_item['quantity'],
            }
            for product_shop_id, cart_item in self.cart.items()
        }

        for product_shop in products:
            goods[str(product_shop.id)]['product'] = product_shop
        yield from goods.values()

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price_rub(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        sum_cart = sum(Money(item['price'], 'RUB').amount * item['quantity'] for item in self.cart.values())
        return Money(sum_cart, 'RUB')

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        total_price_rub = self.get_total_price_rub()
        if self.request.LANGUAGE_CODE == 'ru':
            return total_price_rub
        else:
            return conversion_to_dollar(total_price_rub)

    def clear(self):
        """Удаление корзины из сессии"""
        del self.session[settings.CART_SESSION_ID]

    def validate_goods(self):
        cart_dict_copy = self.cart.copy()

        goods = ProductShop.objects.filter(id__in=cart_dict_copy.keys()).select_related('product')\
            .only('is_active', 'product__is_active')
        for product_shop in goods:
            if product_shop.is_active is False or product_shop.product.is_active is False:
                self.remove(product_shop.id)
