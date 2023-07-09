from django.urls import reverse

from app_shops.tests.test_models import CustomTestCase


class AppShopURLTests(CustomTestCase):
    def test_app_shop_page_url_exists_at_desired_location(self):
        """
        Тест на доступ страницы по URL.
        """
        discount_slug = self.discount.slug
        product_slug = self.product.slug
        shop_slug = self.shop.slug

        pages = ('/',
                 '/catalog/',
                 '/promo/',
                 f'/promo/{discount_slug}/',
                 f'/product/{product_slug}/',
                 '/catalog/compare/',
                 '/about/',
                 f'/store/{shop_slug}/')
        for page in pages:
            response = self.client.get(page)
            error_name = f'Ошибка: нет доступа до страницы {page}'
            self.assertEqual(response.status_code, 200, error_name)

    def test_app_shops_uses_correct_template(self):
        """
        Тест на проверку использования URL-адресом соответствующего шаблона.
        """
        templates_url_names: dict = {
            reverse('home'): 'pages/main.html',
            reverse('catalog'): 'pages/catalog.html',
            reverse('sales'): 'pages/sale.html',
            reverse('discount', args=[self.discount.slug]): 'pages/discount.html',
            reverse('product-detail', args=[self.product.slug]): 'pages/product.html',
            reverse('comparison'): 'pages/comparison.html',
            reverse('about'): 'pages/about.html',
            reverse('store_detail', args=[self.shop.slug]): 'pages/shop.html'}

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                error_name = f'Ошибка: {address} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)
