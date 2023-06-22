from django import forms
from django.utils.translation import gettext_lazy as _


class ReviewForm(forms.Form):
    text = forms.CharField(
        label='',
        error_messages={'required': _('Review text must be entered')},
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': _('Review')}),
        required=True
    )
