from django.urls import path
from .views import RegisterView, LogInView

urlpatterns = [
    path('registr/', RegisterView.as_view(), name='registration'),
    path('login/', LogInView.as_view(), name='login'),
    path('reset_password/stage_1', RegisterView),
    path('reset_password/stage_2', RegisterView)
]
