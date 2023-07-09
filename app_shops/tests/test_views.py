from django.urls import reverse

from app_shops.tests.test_models import CustomTestCase


class AppShopsViewsTest(CustomTestCase):
    def test_home_view_page_show_correct_context(self):
        """
        Шаблон в main.html сформирован с правильным контекстом.
        """
        response = self.client.get(reverse('home'))
        home_view_text = {response.context['top_goods'][0].name: 'product_name',
                          response.context['top_goods'][0].description_short: 'The best product',
                          response.context['top_goods'][0].description_long: 'The best product in the world'}
        for key, value in home_view_text.items():
            self.assertEqual(home_view_text[key], value)

    def test_catalog_view_page_show_correct_content(self):
        """
        Шаблон в catalog.html сформирован с правильным контекстом.
        """
        response = self.client.get(reverse('catalog'))
        catalog_view_text = {response.context['goods'][0].name: 'product_name'}
        for key, value in catalog_view_text.items():
            self.assertEqual(catalog_view_text[key], value)

    def test_sales_view_page_show_correct_context(self):
        """
        Шаблон в sale.html сформирован с правильным контекстом.
        """
        response = self.client.get(reverse('sales'))
        sales_view_text = {response.context['sales'][0].name: 'discount_name',
                           response.context['sales'][0].description_short: 'The best discount',
                           response.context['sales'][0].description_long: 'The best discount in the world'}
        for key, value in sales_view_text.items():
            self.assertEqual(sales_view_text[key], value)

    def test_discount_detail_view_page_show_correct_context(self):
        """
        Шаблон в discount.html сформирован с правильным контекстом.
        """
        response = self.client.get(reverse('discount', args=[self.discount.slug]))
        discount_detail_view_text = {response.context['discount'].name: 'discount_name',
                                     response.context['discount'].description_short: 'The best discount',
                                     response.context['discount'].description_long: 'The best discount in the world'}
        for key, value in discount_detail_view_text.items():
            self.assertEqual(discount_detail_view_text[key], value)

    def test_product_detail_view_page_show_correct_context(self):
        """
        Шаблон в product.html сформирован с правильным контекстом.
        """
        response = self.client.get(reverse('product-detail', args=[self.product.slug]))
        product_detail_view_text = {response.context['product'].name: 'product_name',
                                    response.context['product'].description_short: 'The best product',
                                    response.context['product'].description_long: 'The best product in the world'}
        for key, value in product_detail_view_text.items():
            self.assertEqual(product_detail_view_text[key], value)

    def test_comparison_view_get_correct_object(self):
        """
        Добавление продукта в сессию пользователя на страницу сравнения.
        """
        data = {'add_product': self.product.pk}
        compare_product_count = len(self.client.session.items())
        self.client.post(reverse('comparison'), data=data)
        self.assertEqual(len(self.client.session.items()), compare_product_count + 1)

    def test_shop_detail_view_page_show_correct_context(self):
        """
        Шаблон в shop.html сформирован с правильным контекстом.
        """
        response = self.client.get(reverse('store_detail', args=[self.shop.slug]))
        shop_detail_view_text = {response.context['shop'].name: 'shop_name',
                                 response.context['shop'].description: 'The best shop',
                                 response.context['shop'].mail: 'qwerty@123.com'}
        for key, value in shop_detail_view_text.items():
            self.assertEqual(shop_detail_view_text[key], value)
