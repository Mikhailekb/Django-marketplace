from django import forms
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from app_shops.models.order import DeliveryItem, PaymentItem, DeliveryCategory, PaymentCategory


class OrderForm1(forms.Form):
    """
    Форма оформления заказа. Первый этап
    """
    full_name = forms.CharField(label=_('Full name'), max_length=100, widget=forms.TextInput(
                                    attrs={'class': 'form-input', 'data-validate': 'require', 'id': 'full_name'}))
    phone = forms.CharField(label=_('Tel'), max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-input', 'data-validate': 'require', 'id': 'phone'}))
    email = forms.EmailField(label=_('E-mail'), validators=[validate_email], widget=forms.TextInput(
                                 attrs={'class': 'form-input', 'data-validate': 'require', 'id': 'email'}))


class OrderForm2(forms.ModelForm):
    """
    Форма оформления заказа. Второй этап
    """
    category = forms.ModelChoiceField(queryset=DeliveryCategory.objects.filter(is_active=True), widget=forms.RadioSelect)
    city = forms.CharField(label=_('City'), max_length=100, widget=forms.TextInput(
                               attrs={'class': 'form-input', 'data-validate': 'require', 'id': 'city'}))
    address = forms.CharField(label=_('Address'), widget=forms.Textarea(
                                  attrs={'class': 'form-textarea', 'data-validate': 'require', 'id': 'address'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        return {
            'name': obj.name,
            'value': obj.codename,
        }

    class Meta:
        model = DeliveryItem
        fields = ['category', 'city', 'address']


class OrderForm3(forms.ModelForm):
    """
    Форма оформления заказа. Третий этап
    """
    category = forms.ModelChoiceField(queryset=PaymentCategory.objects.filter(is_active=True),
                                      widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        return {
            'name': obj.name,
            'value': obj.codename,
        }

    class Meta:
        model = PaymentItem
        fields = ('category',)
