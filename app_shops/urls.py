from django.urls import path
from .views import HomeView, CatalogView, ClearCache, SaleView, DiscountDetailView, ProductDetailView, \
    OrderView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('clear_cache/', ClearCache.as_view(), name='clear_cache'),
    path('promo/', SaleView.as_view(), name='sales'),
    path('promo/<slug:promo_slug>/', DiscountDetailView.as_view(), name='discount'),
    path('product/<slug:product_slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('order/checkout/', OrderView.as_view(), name='order'),
]
