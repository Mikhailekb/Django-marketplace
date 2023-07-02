from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from djmoney.money import Money

from app_orders.models import DeliveryCategory, Order
from app_shops.models.category import Category
from app_shops.models.product import Product
from app_shops.models.shop import Shop, ProductShop

name = 'test'
name2 = 'test2'
password = '12test12'
text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit'
email = 'qwerty@mail.ru'
address = 'qwerty'

order_data = {'name': name,
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
        shop = Shop.objects.create(name=name, description=text, mail=email, address=address, slug=name, is_active=True)

        category = Category.objects.create(name=name, slug=name, is_active=True)

        product: Product = Product.objects.create(name=name, description_short=text, description_long=text,
                                                  category=category, slug=name, is_active=True)

        cls.product_shop = ProductShop.objects.create(product=product, shop=shop, count_left=100, count_sold=100,
                                                      price=Money(100, 'RUB'), is_active=True)

        DeliveryCategory.objects.create(name=name, is_active=True, price=Money(200, 'RUB'), codename=name)


class TestOrderView(CustomTestCase):

    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})

    def test_order_url_exists_at_desired_location(self):
        response = self.client.get('/order/checkout/')
        self.assertEqual(response.status_code, 200)

    def test_order_correct_template(self):
        response = self.client.get(reverse('order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/order.html')

    def test_order_no_auth(self):
        self.client.logout()
        response = self.client.get(reverse('order'))
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, '/profile/login?next=/order/checkout/')

    def test_order_without_cart_in_session(self):
        session = self.client.session
        session.pop('cart')
        session.save()

        response = self.client.get(reverse('order'))
        self.assertEqual(response.status_code, 403)

    def test_post_request_with_correct_data(self):
        response = self.client.post(reverse('order'), data=order_data)
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, '/order/payment/bank-card/')

    def test_post_request_with_incorrect_data(self):
        response = self.client.post(reverse('order'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/order.html')


class TestPaymentView(CustomTestCase):

    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})
        self.client.post(reverse('order'), data=order_data)

    def test_payment_url_exists_at_desired_location(self):
        response = self.client.get('/order/payment/bank-card/')
        self.assertEqual(response.status_code, 200)

    def test_payment_uses_correct_template(self):
        response = self.client.get(reverse('payment-bank-card'))
        self.assertTemplateUsed(response, 'pages/payment.html')

    def test_payment_no_auth(self):
        self.client.logout()
        response = self.client.get(reverse('payment-bank-card'))
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, '/profile/login?next=/order/payment/bank-card/')

    def test_payment_without_order_in_session(self):
        session = self.client.session
        session.pop('order')
        session.save()

        response = self.client.get(reverse('payment-bank-card'))
        self.assertEqual(response.status_code, 403)

    def test_post_request_with_correct_data(self):
        response = self.client.post(reverse('payment-bank-card'), data={'account_number': '1234 3456'})
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, '/order/payment/progress/')

    def test_post_request_with_incorrect_data(self):
        response = self.client.post(reverse('payment-bank-card'), data={'account_number': 'qwerty'})
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, reverse('home'))


class TestProgressPaymentView(CustomTestCase):

    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})
        self.client.post(reverse('order'), data=order_data)
        self.client.post(reverse('payment-bank-card'), data={'account_number': '1234 3456'})

    def test_progress_payment_url_exists_at_desired_location(self):
        response = self.client.get('/order/payment/progress/')
        self.assertEqual(response.status_code, 200)

    def test_progress_payment_uses_correct_template(self):
        response = self.client.get(reverse('payment_progress'))
        self.assertTemplateUsed(response, 'pages/progressPayment.html')

    def test_progress_payment_no_auth(self):
        self.client.logout()
        response = self.client.get(reverse('payment_progress'))
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, '/profile/login?next=/order/payment/progress/')

    def test_payment_without_order_in_session(self):
        session = self.client.session
        session.pop('order')
        session.save()

        response = self.client.get(reverse('payment_progress'))
        self.assertEqual(response.status_code, 403)


class TestOrderDetailView(CustomTestCase):
    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})
        self.client.post(reverse('order'), data=order_data)
        self.client.post(reverse('payment-bank-card'), data={'account_number': '1234 3456'})
        self.order = Order.objects.get(buyer_id=1)

    def test_order_detail_url_exists_at_desired_location(self):
        response = self.client.get(f'/order/{self.order.id}/')
        self.assertEqual(response.status_code, 200)

    def test_order_detail_uses_correct_template(self):
        response = self.client.get(reverse('order_detail', args=[self.order.id]))
        self.assertTemplateUsed(response, 'pages/oneorder.html')

    def test_order_detail_no_auth(self):
        self.client.logout()
        response = self.client.get(reverse('order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, f'/profile/login?next=/order/{self.order.id}/')

    def test_order_detail_other_user(self):
        self.client.logout()
        get_user_model().objects.create_user(username=name2, password=password)
        self.client.login(username=name2, password=password)

        response = self.client.get(reverse('order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 403)
