from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from djmoney.money import Money

from app_orders.models import DeliveryCategory, Order
from app_shops.models.category import Category
from app_shops.models.product import Product
from app_shops.models.shop import Shop, ProductShop

name = 'test'
product_name = 'product_name'
name2 = 'test2'
password = '12test12'
text = 'Lorem ipsum dolor sit amet, consecrate disciplining elit'
email = 'qwerty@mail.ru'
email2 = 'qwerty2@mail.ru'
address = 'qwerty'
phone = '+79999999999'
phone2 = '+79999999998'


class CustomTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username=name, password=password)
        shop = Shop.objects.create(name=name, description=text, mail=email,
                                   address=address, slug=name, is_active=True, phone=phone)

        category = Category.objects.create(name=name, slug=name, is_active=True)

        cls.product = product = Product.objects.create(name=product_name, description_short=text, description_long=text,
                                                       category=category, slug=name, is_active=True)

        cls.product_shop = ProductShop.objects.create(product=product, shop=shop, count_left=100, count_sold=100,
                                                      price=Money(100, 'RUB'), is_active=True)

        cls.delivery = delivery = DeliveryCategory.objects.create(name=name, is_active=True, price=Money(200, 'RUB'),
                                                                  codename=name)

        cls.order_data = {'name': name,
                          'phone': phone,
                          'email': email,
                          'city': address,
                          'address': address,
                          'delivery_category': delivery.pk,
                          'payment_category': 'bank-card',
                          }


class TestOrderView(CustomTestCase):

    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})

    def test_order_no_auth(self):
        """Проверка, что неавторизованного пользователя перенаправляет на страницу авторизации"""
        self.client.logout()
        response = self.client.get(reverse('order'))
        self.assertRedirects(response, reverse('account_login') + '?next=/order/checkout/')

    def test_order_without_cart_in_session(self):
        """Проверка, что нельзя зайти на страницу без товаров в корзине"""
        session = self.client.session
        session.pop('cart')
        session.save()

        response = self.client.get(reverse('order'))
        self.assertEqual(response.status_code, 403)

    def test_with_not_active_product(self):
        """Проверка, что нельзя оформить заказ с неактивным товаром"""
        shop = Shop.objects.create(name=name2, description=text, mail=email2,
                                   address=address, slug=name2, is_active=True, phone=phone2)
        product_shop = ProductShop.objects.create(product=self.product, shop=shop, count_left=100, count_sold=100,
                                                  price=Money(100, 'RUB'), is_active=True)

        self.client.post(reverse('cart_add', args=[product_shop.pk]))

        product_shop.is_active = False
        product_shop.save()

        response = self.client.post(reverse('order'), data=self.order_data)
        self.assertEqual(response.status_code, 200)
        response_text = response.context['form'].errors['not_enough_goods']
        self.assertIn(f'{product_name} is not active product', response_text)


class TestPaymentView(CustomTestCase):

    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})
        self.client.post(reverse('order'), data=self.order_data)

    def test_payment_no_auth(self):
        """Проверка, что неавторизованного пользователя перенаправляет на страницу авторизации"""
        self.client.logout()
        response = self.client.get(reverse('payment-bank-card'))
        self.assertRedirects(response, reverse('account_login') + '?next=/order/payment/bank-card/')

    def test_payment_without_order_in_session(self):
        """Проверка, что нельзя зайти на страницу оплаты не оформив заказ"""
        session = self.client.session
        session.pop('order')
        session.save()

        response = self.client.get(reverse('payment-bank-card'))
        self.assertEqual(response.status_code, 403)

    def test_post_request_with_correct_data(self):
        """Проверка работы метода с обработкой post запроса. Post запрос с корректными данными """
        response = self.client.post(reverse('payment-bank-card'), data={'account_number': '1234 3456'})
        self.assertRedirects(response, reverse('payment_progress'))

    def test_post_request_with_incorrect_data(self):
        """Проверка работы метода с обработкой post запроса. Post запрос с некорректными данными """
        response = self.client.post(reverse('payment-bank-card'), data={'account_number': 'qwerty'})
        self.assertRedirects(response, reverse('home'))


class TestProgressPaymentView(CustomTestCase):

    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})
        self.client.post(reverse('order'), data=self.order_data)
        self.client.post(reverse('payment-bank-card'), data={'account_number': '1234 3456'})

    def test_progress_payment_no_auth(self):
        """Проверка, что неавторизованного пользователя перенаправляет на страницу авторизации"""
        self.client.logout()
        response = self.client.get(reverse('payment_progress'))
        self.assertRedirects(response, reverse('account_login') + '?next=/order/payment/progress/')

    def test_payment_without_order_in_session(self):
        """Проверка, что нельзя зайти на страницу оплаты не оформив заказ"""
        session = self.client.session
        session.pop('order')
        session.save()

        response = self.client.get(reverse('payment_progress'))
        self.assertEqual(response.status_code, 403)


class TestOrderDetailView(CustomTestCase):
    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})
        self.client.post(reverse('order'), data=self.order_data)
        self.client.post(reverse('payment-bank-card'), data={'account_number': '1234 3456'})
        self.order = Order.objects.get(buyer_id=self.user.pk)

    def test_order_detail_no_auth(self):
        """Проверка, что неавторизованного пользователя перенаправляет на страницу авторизации"""
        self.client.logout()
        response = self.client.get(reverse('order_detail', args=[self.order.id]))
        self.assertRedirects(response, reverse('account_login') + f'?next=/order/{self.order.id}/')

    def test_order_detail_access_to_page_user_who_made_order(self):
        """Проверка, что пользователь оформивший заказ получает доступ к странице"""
        response = self.client.get(reverse('order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)

    def test_order_detail_other_user_access(self):
        """Проверка, что другие пользователи не могут получить доступ к странице заказа другого пользователя"""
        self.client.logout()
        get_user_model().objects.create_user(username=name2, password=password)
        self.client.login(username=name2, password=password)

        response = self.client.get(reverse('order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 403)
