from django.urls import path

from .views import OrderView, PaymentView, ProgressPaymentView, OrderDetailView, get_delivery_category_info, \
    PaymentSomeOneView

urlpatterns = [
    path('checkout/', OrderView.as_view(), name='order'),
    path('payment/bank-card/', PaymentView.as_view(), name='payment-bank-card'),
    path('payment/some-one/', PaymentSomeOneView.as_view(), name='payment-some-one'),
    path('payment/progress/', ProgressPaymentView.as_view(), name='payment_progress'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('delivery_info/<int:pk>/', get_delivery_category_info, name='order_delivery_info'),
]
