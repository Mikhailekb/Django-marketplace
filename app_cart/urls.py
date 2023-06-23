from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_shop_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_shop_id>/', views.cart_remove, name='cart_remove'),
    path('change/<int:product_shop_id>/<str:type>', views.cart_change_quantity, name='cart_change'),
]
