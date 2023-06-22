from django.urls import path

from .views import OrderView, PaymentView, ProgressPaymentView, OrderDetailView, get_delivery_category_info

urlpatterns = [
    path('checkout/', OrderView.as_view(), name='order'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('payment/progress/', ProgressPaymentView.as_view(), name='payment_progress'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('delivery_info/', get_delivery_category_info, name='order_delivery_info'),
]
