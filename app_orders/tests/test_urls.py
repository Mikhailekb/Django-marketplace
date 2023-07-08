from django.urls import reverse

from app_orders.models import Order
from app_orders.tests.test_views import CustomTestCase

name = 'test'
password = '12test12'


class TestOrdersUrls(CustomTestCase):
    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})
        self.client.post(reverse('order'), data=self.order_data)

    def test_order_and_payment_page(self):
        """Проверка, что страницы находятся по нужному адресу"""
        base_orders_urls = (
            '/order/checkout/',
            '/order/payment/bank-card/',
        )
        self._iterating_over_orders_urls(base_orders_urls)

        self.client.post(reverse('payment-bank-card'), data={'account_number': '1234 3456'})
        order = Order.objects.get(buyer_id=self.user.pk)

        other_orders_urls = (
            '/order/payment/progress/',
            f'/order/{order.id}/',
        )
        self._iterating_over_orders_urls(other_orders_urls)

    def _iterating_over_orders_urls(self, orders_urls):
        for field in orders_urls:
            with self.subTest("Ошибка при попытке зайти на страницу", field=field):
                response = self.client.get(field)
                self.assertEqual(response.status_code, 200)


class TestOrdersTemplates(CustomTestCase):
    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})
        self.client.post(reverse('order'), data=self.order_data)
        self.order = Order.objects.get(buyer_id=self.user.pk)

    def test_correspondence_reverse_and_url(self):
        """Проверка соответствия имени адреса и самого адреса"""
        reverse_and_url: dict[str, str] = {
            reverse('order'): '/order/checkout/',
            reverse('payment-bank-card'): '/order/payment/bank-card/',
            reverse('payment_progress'): '/order/payment/progress/',
            reverse('order_detail', args=[self.order.id]): f'/order/{self.order.id}/',
        }

        for reverse_name, url in reverse_and_url.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse_name, url)

    def test_order_pages_uses_correct_templates(self):
        """Проверка, что страницы используют корректный шаблон"""
        base_reverse_and_template = {
            reverse('order'): 'pages/order.html',
            reverse('payment-bank-card'): 'pages/payment.html',
        }
        self._iterating_over_reverse_and_template(base_reverse_and_template)

        self.client.post(reverse('payment-bank-card'), data={'account_number': '1234 3456'})

        other_reverse_and_template = {
            reverse('payment_progress'): 'pages/progressPayment.html',
            reverse('order_detail', args=[self.order.id]): 'pages/oneorder.html',
        }
        self._iterating_over_reverse_and_template(other_reverse_and_template)

    def _iterating_over_reverse_and_template(self, reverse_and_template):
        for reverse_name, template in reverse_and_template.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
