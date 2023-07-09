from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from app_shops.models.category import Category
from app_shops.models.product import Product
from app_shops.models.product import Review

User = get_user_model()
name = 'test'
password = 'password'
text = 'The best product'
form_data = {'text': text}


class ReviewFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.category = Category.objects.create(name=name, slug=name, is_active=True)
        self.product = Product.objects.create(name=name, description_short=text, description_long=text,
                                              category=self.category, slug=name, is_active=True)

    def test_create_review_redirect(self):
        """
        Тестирование редиректа на страницу авторизации неавторизованного пользователя.
        """
        response = self.guest_client.post(reverse('product-detail', args=[self.product.slug]), data=form_data)
        self.assertRedirects(response, '/profile/accounts/login/?next=/product/test/')

    def test_correct_review(self):
        """
        Тестирование увеличения отзывов при отправке формы и создании отзыва с заданным текстом.
        """
        self.review_count = Review.objects.count()
        self.authorized_client.post(reverse('product-detail', args=[self.product.slug]), data=form_data)
        self.assertEqual(Review.objects.count(), self.review_count + 1)
        self.assertTrue(Review.objects.filter(text='The best product').exists())
