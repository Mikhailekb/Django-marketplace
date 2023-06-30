from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from app_users.models import Profile


class SignupViewTest(TestCase):
    def test_exists_page(self):
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')

    def test_correct(self):
        response = self.client.post(reverse('account_signup'), {'username': 'test', 'email': 'test@gmail.com', 'password1': 'test3267'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(Profile.objects.all().count(), 1)

    def test_wrong_username(self):
        response = self.client.post(reverse('account_signup'), {'username': '', 'email': 'test@gmail.com', 'password1': 'test7359'})
        self.assertNotEqual(response.status_code, 302)
        self.assertNotEqual(User.objects.all().count(), 1)

    def test_wrong_email(self):
        response = self.client.post(reverse('account_signup'), {'username': 'test', 'email': 'test', 'password1': 'test7359'})
        self.assertNotEqual(response.status_code, 302)
        self.assertNotEqual(User.objects.all().count(), 1)

    def test_wrong_password(self):
        response = self.client.post(reverse('account_signup'), {'username': 'test', 'email': 'test@gmail.com', 'password1': ''})
        self.assertNotEqual(response.status_code, 302)
        self.assertNotEqual(User.objects.all().count(), 1)



