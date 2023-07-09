from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from app_users.models import Profile


class SignupViewTest(TestCase):
    def test_exists_page(self):

        """Проверка наличия страницы регистрации"""

        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')

    def test_correct(self):

        """Проверка регистрации валидного пользователя"""

        response = self.client.post(reverse('account_signup'), {'username': 'test', 'email': 'test@gmail.com', 'password1': 'test3267'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(Profile.objects.all().count(), 1)
        self.assertRedirects(response, reverse('home'))

    def test_wrong_username(self):

        """Проверка регистрации невалидного пользователя"""

        response = self.client.post(reverse('account_signup'), {'username': '', 'email': 'test@gmail.com', 'password1': 'test7359'})
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(get_user_model().objects.all().count(), 1)
        self.assertFalse(response.context_data['form'].is_valid())

    def test_wrong_email(self):

        """Проверка регистрации невалидного пользователя"""

        response = self.client.post(reverse('account_signup'), {'username': 'test', 'email': 'test', 'password1': 'test7359'})
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(get_user_model().objects.all().count(), 1)
        self.assertFalse(response.context_data['form'].is_valid())

    def test_wrong_password(self):

        """Проверка регистрации невалидного пользователя"""

        response = self.client.post(reverse('account_signup'), {'username': 'test', 'email': 'test@gmail.com', 'password1': ''})
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(get_user_model().objects.all().count(), 1)
        self.assertFalse(response.context_data['form'].is_valid())



