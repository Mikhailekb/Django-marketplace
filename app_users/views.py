from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .forms import RegisterForm, ResetPassStage1Form, ResetPassStage2Form, AuthForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.core.mail import send_mail


class RegisterView(FormView):
    """
    Представление для регистрации пользователя
    """
    form_class = RegisterForm
    template_name = "pages/registr.html"
    success_url = reverse_lazy('login')
    context_object_name = 'form'

    def form_valid(self, form):
        user = form.save()
        authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
        login(self.request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
        return HttpResponseRedirect(reverse_lazy('login'))


class LogInView(LoginView):
    """Представление для логина пользователя"""
    template_name = 'pages/login.html'
    form_class = AuthForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')


class ResetPassStage1(LoginRequiredMixin, FormView):
    """Представление для восстановления пароля. Ввод Email"""
    template_name = 'pages/e-mail.html'
    form_class = ResetPassStage1Form
    success_url = reverse_lazy('reset_1')

    def form_valid(self, form):
        response = super().form_valid(form)
        if User.objects.get(email=form.cleaned_data['email']).email == self.request.user.email:
            send_mail(
                subject="",
                message="Для восстановления пароля перейдите по ссылке и введите новый пароль\n"
                        "http://127.0.0.1:8000/profile/reset_password/stage_2",
                from_email="local",
                recipient_list=[form.cleaned_data['email']],
                fail_silently=False,
            )
        return response


class ResetPassStage2(FormView):
    """Представление для восстановления пароля. Ввод нового пароля"""
    form_class = ResetPassStage2Form
    template_name = 'pages/password.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = User.objects.get(username=self.request.user.username)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)




