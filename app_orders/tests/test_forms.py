from django.urls import reverse

from app_orders.tests.test_views import CustomTestCase

name = 'test'
password = '12test12'
email = 'qwerty@mail.ru'
address = 'qwerty'


class TestOrderForm(CustomTestCase):
    def setUp(self):
        self.client.defaults['HTTP_ACCEPT_LANGUAGE'] = 'ru'
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
        """Проверка работы, если данные в форме корректные"""
        response = self.client.post(reverse('order'), data=self.order_data)
        self.assertRedirects(response, reverse('payment-bank-card'))

    def test_without_one_required_field(self):
        """Проверка работы, если в форме не указано одно обязательное поле"""
        required_fields = ('name', 'phone', 'email', 'city', 'address', 'delivery_category', 'payment_category')
        for field in required_fields:
            order_data_copy = self.order_data.copy()
            order_data_copy.pop(field)

            response = self.client.post(reverse('order'), data=order_data_copy)
            with self.subTest("Запрос был успешен без указания обязательного поля", field=field):
                self.assertFormError(response=response, form='form', field=field, errors='Обязательное поле.')

    def test_email_validator(self):
        """Проверка работы валидации электронной почты"""
        self.order_data['email'] = 'testmail.org'
        response = self.client.post(reverse('order'), data=self.order_data)
        self.assertFormError(response=response, form='form', field='email',
                             errors='Введите правильный адрес электронной почты.')

    def test_phone_validator(self):
        """Проверка работы валидации номера телефона"""
        self.order_data['phone'] = '123456789'
        response = self.client.post(reverse('order'), data=self.order_data)
        self.assertFormError(response=response, form='form', field='phone',
                             errors='Введите корректный номер телефона (например, +12125552368).')

    def test_delivery_category_validator(self):
        """Проверка работы валидации выбора способа доставки"""
        self.order_data['delivery_category'] = -1
        response = self.client.post(reverse('order'), data=self.order_data)
        self.assertFormError(response=response, form='form', field='delivery_category',
                             errors='Выберите корректный вариант. Вашего варианта нет среди допустимых значений.')

    def test_payment_category_validator(self):
        """Проверка работы валидации выбора способа оплаты"""
        self.order_data['payment_category'] = 'qwerty'
        response = self.client.post(reverse('order'), data=self.order_data)
        self.assertFormError(response=response, form='form', field='payment_category',
                             errors='Выберите корректный вариант. qwerty нет среди допустимых значений.')
