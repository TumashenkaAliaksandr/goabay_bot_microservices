# forms.py
from django import forms
from tinymce.widgets import TinyMCE

from bot_app.models import Product, NewsletterSubscription, Review


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



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['author_name', 'review_text', 'rating']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя',
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Ваш отзыв',
            }),
            'rating': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(5, 0, -1)]),
        }
