from django.urls import path, include
from .views import ResetPassStage1, ResetPassStage2, ProfileEditView, AccountView, OrderListView

urlpatterns = [
    path('reset_password/stage_1/', ResetPassStage1.as_view(), name='reset_1'),
    path('reset_password/stage_2/', ResetPassStage2.as_view(), name='reset_2'),
    path('edit/', ProfileEditView.as_view(), name='edit'),
    path('account/', AccountView.as_view(), name='account'),
    path('orders/', OrderListView.as_view(), name='orders'),
    path('accounts/', include('allauth.urls')),
]