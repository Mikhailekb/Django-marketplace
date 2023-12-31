from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from .forms import RegisterForm, ResetPassStage1Form, ResetPassStage2Form, AuthForm, UserEditForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, UpdateView
from django.core.mail import send_mail
from .models import Profile


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
        login(self.request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
        return super().form_valid(form)


class LogInView(LoginView):
    """Представление для логина пользователя"""
    template_name = 'pages/login.html'
    form_class = AuthForm
    success_url = reverse_lazy('home')


class ResetPassStage1(LoginRequiredMixin, FormView):
    """Представление для восстановления пароля. Ввод Email"""
    template_name = 'pages/e-mail.html'
    form_class = ResetPassStage1Form
    success_url = reverse_lazy('reset_1')

    def form_valid(self, form):
        response = super().form_valid(form)
        email = form.cleaned_data['email']
        if User.objects.get(email=email):
            send_mail(
                subject="",
                message="Для восстановления пароля перейдите по ссылке и введите новый пароль\n"
                        "http://127.0.0.1:8000/profile/reset_password/stage_2",
                from_email="local",
                recipient_list=[email],
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


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'pages/profile.html'
    model = Profile
    fields = ['avatar', 'name', 'phone']
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        return reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        self.object = self.request.user.profile
        if not self.request.user.username == self.kwargs['slug']:
            return HttpResponseRedirect(reverse_lazy('login'))
        return self.render_to_response(self.get_context_data(object=self.object))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_form = UserEditForm()
        user_form.fields['email'].widget.attrs['value'] = self.request.user.email
        context['user_form'] = user_form
        context['image'] = Profile.objects.get(user__username=self.request.user).avatar
        if 'errors' in kwargs:
            context['error_form'] = kwargs['errors']
        return context

    def form_valid(self, form, **kwargs):
        user_form = UserEditForm(self.request.POST, instance=self.request.user)
        profile = self.get_object()
        if user_form.is_valid():
            form.save()
            user_form.save()
            user = authenticate(username=user_form.cleaned_data['email'], password=user_form.cleaned_data['password2'])
            login(self.request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            return redirect('edit', slug=profile.slug)
        return self.render_to_response(self.get_context_data(errors=user_form, **kwargs))


class AccountView(DetailView):
    template_name = 'pages/account.html'
    model = Profile
    fields = ['avatar', 'name']
    slug_field = 'name'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



