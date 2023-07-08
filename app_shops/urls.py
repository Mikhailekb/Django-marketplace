from django.urls import path

from .views import HomeView, CatalogView, SaleView, DiscountDetailView, ProductDetailView, ComparisonView, \
    AboutUsView, ShopDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('promo/', SaleView.as_view(), name='sales'),
    path('promo/<slug:promo_slug>/', DiscountDetailView.as_view(), name='discount'),
    path('product/<slug:product_slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('catalog/compare/', ComparisonView.as_view(), name='comparison'),
    path('about/', AboutUsView.as_view(), name='about'),
    path('store/<slug:store_slug>/', ShopDetailView.as_view(), name='store_detail')
]
