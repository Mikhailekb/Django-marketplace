from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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
