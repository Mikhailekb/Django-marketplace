from django import forms
from django.core.validators import validate_email
from django.db import ProgrammingError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

from .models import DeliveryCategory, PaymentItem


class OrderForm(forms.Form):
    """
    Форма оформления заказа
    """
    delivery_qs = DeliveryCategory.objects.filter(is_active=True)

    try:
        initial_delivery = delivery_qs.first()
    except ProgrammingError:
        initial_delivery = None

    name = forms.CharField(label=_('Full name'),
                           max_length=100,
                           widget=forms.TextInput(attrs={'class': 'form-input',
                                                         'data-validate': 'require',
                                                         'id': 'name'}))
    phone = PhoneNumberField(label=_('Tel'),
                             widget=forms.TextInput(attrs={'class': 'form-input',
                                                           'data-validate': 'require',
                                                           'id': 'phone'}))
    email = forms.EmailField(label=_('E-mail'),
                             validators=[validate_email],
                             widget=forms.TextInput(attrs={'class': 'form-input',
                                                           'data-validate': 'require mail',
                                                           'id': 'email'}))
    delivery_category = forms.ModelChoiceField(queryset=delivery_qs,
                                               widget=forms.RadioSelect,
                                               initial=initial_delivery)
    city = forms.CharField(label=_('City'),
                           max_length=100,
                           widget=forms.TextInput(attrs={'class': 'form-input',
                                                         'data-validate': 'require',
                                                         'id': 'city'}))
    address = forms.CharField(label=_('Address'),
                              max_length=256,
                              widget=forms.Textarea(attrs={'class': 'form-textarea',
                                                           'data-validate': 'require',
                                                           'id': 'address'}))
    comment = forms.CharField(label=_('Comment'),
                              required=False,
                              max_length=500,
                              widget=forms.Textarea(attrs={'class': 'form-textarea',
                                                           'id': 'comment'}))
    payment_category = forms.ChoiceField(choices=PaymentItem.PAYMENT_CATEGORY,
                                         widget=forms.RadioSelect,
                                         initial=PaymentItem.PAYMENT_CATEGORY[0][0])
    is_free_delivery = forms.BooleanField(required=False)
