from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

name = 'test'
email = 'test@example.com'
password = '12test12'
password2 = '21test21'


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username=name, email=email, password=password)


class TestResetPass1(TestCase):

    def test_exists_page(self):

        """Проверка наличия 1-ой страницы восстановления пароля"""

        response = self.client.get(reverse('reset_1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/e-mail.html')

    def test_send_email(self):

        """Проверка отправки сообщения на нужный e-mail"""

        mail.send_mail('', f"Для восстановления пароля перейдите по ссылке и введите новый пароль\n"
                        f"http://127.0.0.1:8000/profile/reset_password/stage_2?email=test@example.com/",
                       'local', ['test@example.com'],
                       fail_silently=False)
        self.assertEqual(len(mail.outbox), 1)


class TestResetPass2(BaseTestCase):

    def test_exists_page(self):

        """Проверка наличия 2-ой страницы восстановления пароля"""

        response = self.client.get(reverse('reset_2') + f'?email={email}', {'password': password2})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/password.html')

    def test_redirect_page(self):

        """Проверка редиректа на следующую страницу"""

        response = self.client.post(reverse('reset_2') + f'?email={email}', {'password': password2})
        self.assertRedirects(response, reverse('home'))

    def test_reset_pass(self):

        """Проверка изменения пароля"""

        self.client.post(reverse('reset_2') + f'?email={email}', {'password': password2})
        self.client.logout()
        self.assertTrue(self.client.login(username=name, password=password2))

