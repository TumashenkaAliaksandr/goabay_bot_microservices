from django import forms
from .models import Product, News, NewsImage, AboutUs
from django.utils.text import slugify


#
# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['name', 'desc', 'price', 'rating', 'brand', 'category', 'image']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'desc': forms.Textarea(attrs={'class': 'form-control'}),
#             'price': forms.NumberInput(attrs={'class': 'form-control'}),
#             'rating': forms.NumberInput(attrs={'class': 'form-control'}),
#             'brand': forms.TextInput(attrs={'class': 'form-control'}),
#             'category': forms.TextInput(attrs={'class': 'form-control'}),
#             'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
#         }


class NewsImageForm(forms.ModelForm):
    class Meta:
        model = NewsImage
        fields = ["image", "description"]


class AboutUsForm(forms.ModelForm):
    class Meta:
        model = AboutUs
        fields = ['title', 'content', 'image']