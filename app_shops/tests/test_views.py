from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from djmoney.money import Money

from app_orders.models import DeliveryCategory
from app_shops.models.category import Category
from app_shops.models.discount import Discount
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

        cls.product = Product.objects.create(name=name, description_short=text, description_long=text,
                                         category=category, slug=name, is_active=True)

        cls.discount = Discount.objects.create(name=name, description_short=text, description_long=text,
                                               slug=name, shop=shop, discount_percentage=10,
                                               date_start=timezone.now(), is_active=True)

        cls.product_shop = ProductShop.objects.create(product=cls.product, shop=shop, count_left=100, count_sold=100,
                                                      price=Money(100, 'RUB'), is_active=True, discount=cls.discount)

        DeliveryCategory.objects.create(name=name, is_active=True, price=Money(200, 'RUB'), codename=name)


class TestHomeView(CustomTestCase):

    def test_home_page_url_exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_uses_page_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/main.html')


class TestCatalogView(CustomTestCase):

    def test_catalog_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/')
        self.assertEqual(response.status_code, 200)

    def test_catalog_uses_correct_template(self):
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/catalog.html')


class TestSaleView(CustomTestCase):

    def test_sale_url_exists_at_desired_location(self):
        response = self.client.get('/promo/')
        self.assertEqual(response.status_code, 200)

    def test_sale_uses_correct_template(self):
        response = self.client.get(reverse('sales'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/sale.html')


class TestDiscountDetailView(CustomTestCase):

    def test_sale_url_exists_at_desired_location(self):
        discount_slug = self.discount.slug
        response = self.client.get(f'/promo/{discount_slug}/')
        self.assertEqual(response.status_code, 200)

    def test_sale_uses_correct_template(self):
        discount_url = self.discount.get_absolute_url()
        response = self.client.get(discount_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/discount.html')


class TestProductDetailView(CustomTestCase):
    def test_product_detail_url_exists_at_desired_location(self):
        product_slug = self.product.slug
        response = self.client.get(f'/product/{product_slug}/')
        self.assertEqual(response.status_code, 200)

    def test_product_detail_uses_correct_template(self):
        product_url = self.product.get_absolute_url()
        response = self.client.get(product_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/product.html')


class TestComparisonView(CustomTestCase):
    def test_comparison_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/compare/')
        self.assertEqual(response.status_code, 200)

    def test_comparison_uses_correct_template(self):
        response = self.client.get(reverse('comparison'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/comparison.html')


class TestAboutUsView(CustomTestCase):
    def test_about_us_url_exists_at_desired_location(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)

    def test_about_us_uses_correct_template(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/about.html')

