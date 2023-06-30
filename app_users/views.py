from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .forms import ResetPassStage1Form, ResetPassStage2Form, UserEditForm
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, UpdateView, ListView
from django.core.mail import send_mail
from .models import Profile
from app_shops.models.order import Order


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
    """Представление, отображающее форму с данными пользователя и позволяющее её изменить"""
    template_name = 'pages/profile.html'
    model = Profile
    fields = ['avatar', 'name', 'phone']

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_form = UserEditForm()
        user_form.fields['email'].widget.attrs['value'] = self.request.user.email
        context['user_form'] = user_form
        profile = Profile.objects.get(user__username=self.request.user)
        if profile.avatar:
            context['image'] = profile.avatar
        if 'errors' in kwargs:
            context['error_form'] = kwargs['errors']
        return context

    def form_valid(self, form, **kwargs):
        user_form = UserEditForm(self.request.POST, instance=self.request.user)
        if user_form.is_valid():
            form.save()
            username = user_form.cleaned_data['email']
            password = user_form.cleaned_data['password2']
            if password:
                user_form.save()
                user = authenticate(username=username, password=password)
                login(self.request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            else:
                user = User.objects.get(username=self.request.user)
                user.email = username
                user.save()
                user = authenticate(username=username, password=self.request.user.password)
                login(self.request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            return self.render_to_response(self.get_context_data(success_profile=True, **kwargs))
        return self.render_to_response(self.get_context_data(errors=user_form, **kwargs))


class AccountView(DetailView):
    """Представление для отображения детальной информации о пользователе"""
    template_name = 'pages/account.html'
    model = Profile
    fields = ['avatar', 'name']
    slug_field = 'name'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user__username=self.request.user)
        if profile.avatar:
            context['image'] = profile.avatar
        context['order'] = Order.objects.filter(buyer__username=self.request.user)[:3]
        return context


class OrderListView(LoginRequiredMixin, ListView):
    """Представление для отображения списка заказов пользователя"""
    template_name = 'pages/historyorder.html'
    model = Order
    context_object_name = 'order_list'

    def get_queryset(self):
        return Order.objects.filter(buyer__username=self.request.user)[:20]




