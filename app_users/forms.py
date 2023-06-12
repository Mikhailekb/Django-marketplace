from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from app_users.models import Profile


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
    class Meta:
        fields = ['username', 'password']

    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': "user-input", "name":"name", "id": "name", "placeholder": "Email", 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"name": "pass", "id": "name", "placeholder": "*********"}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 8:
            return ValidationError("Некорректная длина поля")
        return username


class ResetPassStage1Form(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': "user-input", 'name': "login", 'id': "name", 'placeholder': "E-mail"}))

    def clean_email(self):
        email = self.cleaned_data['email']

        if not User.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError("Данного email не существует!")
        return email


class ResetPassStage2Form(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': "pass", 'placeholder': "Пароль"})
    )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'avatar', 'name', 'slug']

    def clean_name(self):
        name = self.cleaned_data.get("name")

        if not len(name.split()) == 3:
            raise ValidationError("Введите ФИО полностью")
        return name


class UserEditForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-input", "id": "mail", "type": "text", "data-validate":"require"}))
    password1 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), required=False)
    password2 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), required=False)

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if (password1 and not password2) or (not password1 and password2):
            self.add_error('password2', "Заполните оба поля")

        elif password1 and password2 and password1 != password2:
            self.add_error('password2', "Пароли не совпадают")

        elif password1 and len(password1) < 8:
            self.add_error('password1', "Длина пароля должна составлять минимум 8 символов")

        elif password2 and len(password2) < 8:
            self.add_error('password2', "Длина пароля должна составлять минимум 8 символов")

        return self.cleaned_data
