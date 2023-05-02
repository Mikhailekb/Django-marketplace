from django import forms
from django.utils.translation import gettext_lazy as _


class FilterGoodsForm(forms.Form):
    """Форма для фильтрации товаров"""

    price = forms.CharField()
    name = forms.CharField(required=False, widget=forms.TextInput(
                attrs={'class': "form-input form-input_full", 'id': "title", 'placeholder': "Название"}))
    in_stock = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    free_shipping = forms.BooleanField(required=False, widget=forms.CheckboxInput())

