from django.contrib.auth import authenticate, login
from .forms import RegisterForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView


class RegisterView(CreateView):
    """
    Представление для регистрации пользователя
    """
    form_class = RegisterForm
    template_name = "pages/registr.html"
    success_url = reverse_lazy('home')
    context_object_name = 'form'

    def form_valid(self, form):
        response = super().form_valid(form)

        name = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(
            self.request,
            username=name,
            password=password
        )

        login(request=self.request, user=user)
        return response


class LogInView(LoginView):
    """Представление для логина пользователя"""
    template_name = 'pages/login.html'
    redirect_authenticated_user = True

