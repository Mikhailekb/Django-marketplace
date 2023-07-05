from django.urls import reverse

from app_orders.tests.test_views import CustomTestCase

name = 'test'
password = '12test12'
email = 'qwerty@mail.ru'
address = 'qwerty'


class TestOrderForm(CustomTestCase):
    def setUp(self):
        self.client.login(username=name, password=password)
        self.client.post(reverse('cart_add', args=[self.product_shop.pk]), data={'quantity': 10})

        self.order_data = {'name': name,
                           'phone': '+79999999999',
                           'email': email,
                           'city': address,
                           'address': address,
                           'delivery_category': 1,
                           'payment_category': 'bank-card',
                           }

    def test_with_correct_data(self):
        response = self.client.post(reverse('order'), data=self.order_data)
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, '/order/payment/bank-card/')

    def test_without_one_required_field(self):
        required_fields = ('name', 'phone', 'email', 'city', 'address', 'delivery_category', 'payment_category')
        for field in required_fields:
            order_data_copy = self.order_data.copy()
            order_data_copy.pop(field)

            response = self.client.post(reverse('order'), data=order_data_copy)
            response_text = response.context['form'].errors[field]
            with self.subTest("Запрос был успешен без указания обязательного поля", i=field):
                self.assertIn('This field is required.', response_text)

    def test_email_validator(self):
        self.order_data['email'] = 'testmail.org'
        response = self.client.post(reverse('order'), data=self.order_data)
        response_text = response.context['form'].errors['email']
        self.assertIn('Enter a valid email address.', response_text)

    def test_phone_validator(self):
        self.order_data['phone'] = '123456789'
        response = self.client.post(reverse('order'), data=self.order_data)
        response_text = response.context['form'].errors['phone']
        self.assertIn('Введите корректный номер телефона (например, +12125552368).', response_text)

    def test_delivery_category_validator(self):
        self.order_data['delivery_category'] = -1
        response = self.client.post(reverse('order'), data=self.order_data)
        response_text = response.context['form'].errors['delivery_category']
        self.assertIn('Select a valid choice. That choice is not one of the available choices.', response_text)

    def test_payment_category_validator(self):
        self.order_data['payment_category'] = 'qwerty'
        response = self.client.post(reverse('order'), data=self.order_data)
        response_text = response.context['form'].errors['payment_category']
        self.assertIn('Select a valid choice. qwerty is not one of the available choices.', response_text)
