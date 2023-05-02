from django.urls import path
from .views import HomeView, CatalogView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('catalog/<slug:category_slug>/', CatalogView.as_view(), name='catalog'),
]