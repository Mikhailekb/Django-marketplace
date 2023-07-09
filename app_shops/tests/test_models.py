from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from djmoney.money import Money

from app_orders.models import DeliveryCategory
from app_shops.models.category import Category
from app_shops.models.discount import Discount
from app_shops.models.product import Product
from app_shops.models.shop import Shop, ProductShop

name = 'test'
name2 = 'test2'
password = '12test12'
text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit'
email = 'qwerty@mail.ru'
address = 'qwerty'

shops_data = {'name': name,
              'phone': '+79999999999',
              'email': email,
              'city': address,
              'address': address,
              'delivery_category': 1,
              'payment_category': 'bank-card',
              }


class CustomTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username=name, password=password)
        cls.shop = Shop.objects.create(name=name, description=text, mail=email, address=address, slug=name,
                                       is_active=True)
        cls.category = Category.objects.create(name=name, slug=name, is_active=True)

        cls.product = Product.objects.create(name=name, description_short=text, description_long=text,
                                             category=cls.category, slug=name, is_active=True)

        cls.discount = Discount.objects.create(name=name, description_short=text, description_long=text,
                                               slug=name, shop=cls.shop, discount_percentage=10,
                                               date_start=timezone.now(), is_active=True)

        cls.product_shop = ProductShop.objects.create(product=cls.product, shop=cls.shop, count_left=100,
                                                      count_sold=100,
                                                      price=Money(100, 'RUB'), is_active=True, discount=cls.discount)

        DeliveryCategory.objects.create(name=name, is_active=True, price=Money(200, 'RUB'), codename=name)


class AppShopModelsTest(CustomTestCase):
    def test_shop_model_correct_work(self):
        """
        Проврерка добавления обьектов в модели приложения
        """
        shop_model = Shop.objects.get(slug=self.shop.slug)
        product_model = Product.objects.get(slug=self.product.slug)
        category_model = Category.objects.get(slug=self.category.slug)
        discount_model = Discount.objects.get(slug=self.discount.slug)
        productshop_model = ProductShop.objects.get(product=self.product)
        self.assertTrue(shop_model.name == shops_data['name'])
        self.assertTrue(product_model.name == shops_data['name'])
        self.assertTrue(category_model.name == shops_data['name'])
        self.assertTrue(discount_model.name == shops_data['name'])
        self.assertTrue(productshop_model.product == self.product)
