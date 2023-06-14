from django.urls import path, include
from .views import RegisterView, LogInView, ResetPassStage1, ResetPassStage2, ProfileEditView, AccountView

urlpatterns = [
    path('registr/', RegisterView.as_view(), name='registration'),
    path('login/', LogInView.as_view(), name='login'),
    path('reset_password/stage_1', ResetPassStage1.as_view(), name='reset_1'),
    path('reset_password/stage_2', ResetPassStage2.as_view(), name='reset_2'),
    path('<slug:slug>/edit', ProfileEditView.as_view(), name='edit'),
    path('<slug:slug>/account', AccountView.as_view(), name='account'),
    path('accounts/', include('allauth.urls')),
]
