from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
import tempfile

from djmoney.money import Money

from app_orders.models import DeliveryCategory, Order
from app_shops.models.category import Category
from app_shops.models.product import Product
from app_shops.models.shop import Shop, ProductShop

name = 'test'
password = 'test626732'
phone = '+79999999999'
email = 'test@example.com'
surname = 'Name Name Name'
product_name = 'product_name'
name2 = 'test2'
text = 'Lorem ipsum dolor sit amet, consecrate disciplining elit'
email2 = 'qwerty2@mail.ru'
address = 'qwerty'
phone2 = '+79999999998'


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = user = get_user_model().objects.create_user(username=name, email=email, password=password)
        shop = Shop.objects.create(name=name, description=text, mail=email,
                                   address=address, slug=name, is_active=True, phone=phone)

        category = Category.objects.create(name=name, slug=name, is_active=True)

        cls.product = product = Product.objects.create(name=product_name, description_short=text, description_long=text,
                                                       category=category, slug=name, is_active=True)

        cls.product_shop = ProductShop.objects.create(product=product, shop=shop, count_left=100, count_sold=100,
                                                      price=Money(100, 'RUB'), is_active=True)

        cls.delivery = delivery = DeliveryCategory.objects.create(name=name, is_active=True, price=Money(200, 'RUB'),
                                                                  codename=name)

        cls.order_data = {'buyer': user,
                          'phone': phone,
                          'email': email,
                          'city': address,
                          'address': address,
                          'delivery_category': delivery,
                          }


class AccountViewTest(BaseTestCase):

    def setUp(self):
        self.client.login(username=name, password=password)

    def test_exists_page(self):

        """Проверка наличия страницы аккаунта"""
        response = self.client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/account.html')


class ProfileViewTest(BaseTestCase):

    def setUp(self):
        self.client.login(username=name, password=password)

    def test_exists_page(self):

        """Проверка наличия страницы профиля"""
        response = self.client.get(reverse('edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/profile.html')

    def test_edit_user(self):

        """Проверка изменения данных пользователя в профиле"""

        img = tempfile.NamedTemporaryFile(suffix=".jpg").name

        response = self.client.post(reverse('edit'), {'avatar': img, 'name': surname, 'phone': phone, 'email': email,
                                                      'password1': password, 'password2': password})

        self.assertTrue(response.context_data['form'].is_valid)
        self.assertEqual(response.status_code, 200)


class OrderListViewTest(BaseTestCase):

    def setUp(self):
        self.client.login(username=name, password=password)

    def test_exists_page(self):

        """Проверка наличия страницы истории заказов"""

        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/historyorder.html')

    def test_orders_list(self):

        """Проверка вывода списка заказов на странице"""

        for order in range(10):
            Order.objects.create(**self.order_data)
        response = self.client.get(reverse('orders'))
        self.assertEqual(len(response.context['order_list']), 10)







