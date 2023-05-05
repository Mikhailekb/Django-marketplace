from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password',)

        widgets = {
            'username': forms.TextInput(
                attrs={'class': "user-input", 'name': "name", 'id': "name", 'placeholder': "Имя"}
            ),
            'email': forms.EmailInput(
                attrs={'class': "user-input", 'name': "login", 'id': "email",
                       'placeholder': "E-mail"
                }
            ),
            'password': forms.PasswordInput(
                attrs={'name': "pass", 'id': "pass", 'placeholder': "Пароль"}
            )
        }

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError("Данный email уже существует!")
        return email


class AuthForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': "user-input", "name":"name", "id": "name", "placeholder": "Email", 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"name": "pass", "id": "name", "placeholder": "*********"}))

    class Meta:
        fields = []


class ResetPassStage1Form(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': "user-input", 'name': "login", 'id': "name", 'placeholder': "E-mail"}))

    def clean_email(self):
        email = self.cleaned_data['email']

        if not User.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError("Данного email не существует!")
        return email


class ResetPassStage2Form(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'name': "pass", 'id': "pass", 'placeholder': "Пароль"})
    )

