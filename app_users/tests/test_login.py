from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

username = 'testuser'
email = 'testuser@example.com'
password = '1password1'


class LoginViewTest(TestCase):
    def setUp(self):
        self.data = {
            'username': username,
            'email': email,
            'password': password}
        User.objects.create_user(**self.data)

    def test_exists_page(self):

        """Проверка наличия страницы логина"""

        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_correct_login(self):

        """Проверка корректности работы логина"""

        response = self.client.post(reverse('account_login'), {'login': email, 'password': password})
        self.assertTrue(response.context['user'].is_authenticated)