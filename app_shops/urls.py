from django.urls import path

from .views import HomeView, CatalogView, ClearCache, SaleView, DiscountDetailView, ProductDetailView, ComparisonView, ShopDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('clear_cache/', ClearCache.as_view(), name='clear_cache'),
    path('promo/', SaleView.as_view(), name='sales'),
    path('promo/<slug:promo_slug>/', DiscountDetailView.as_view(), name='discount'),
    path('product/<slug:product_slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('catalog/compare/', ComparisonView.as_view(), name='comparison'),
    path('shop/<int:pk>/', ShopDetailView.as_view(), name='shop_detail')
]
