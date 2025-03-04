# forms.py
from django import forms
from tinymce.widgets import TinyMCE

from bot_app.models import Product
from .models import NewsletterSubscription

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email', 'permission']


class ProductForm(forms.ModelForm):
    """Форма для админки Product с использованием TinyMCE."""
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'additional_description': TinyMCE(),
            'desc': TinyMCE(),
        }
