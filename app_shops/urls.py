from django.urls import path
from .views import HomeView, CatalogView, ClearCache, SaleView, DiscountDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('clear_cache/', ClearCache.as_view(), name='clear_cache'),
    path('sales/', SaleView.as_view(), name='sales'),
    path('sales/<slug:discount_slug>/', DiscountDetailView.as_view(), name='discount'),
]