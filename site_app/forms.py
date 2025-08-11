# forms.py
from django import forms
from tinymce.widgets import TinyMCE
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from bot_app.models import Product, NewsletterSubscription, Review, UserProfile


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



class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address here...'})
    )
    telephone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telephone'})
    )
    newsletter = forms.ChoiceField(
        choices=((1, 'Yes'), (0, 'No')),
        widget=forms.RadioSelect,
        initial=0,
        label='Subscribe'
    )
    agree = forms.BooleanField(label='I have read and agree to the Privacy Policy')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Пароли не совпадают.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            # здесь можно сохранять профиль (телефон, подписку) в отдельную модель
        return user


class AccountDetailsForm(forms.ModelForm):
    password_current = forms.CharField(label='Current password', widget=forms.PasswordInput, required=False)
    password_new = forms.CharField(label='New password', widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(label='Confirm new password', widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        pw_new = cleaned_data.get('password_new')
        pw_confirm = cleaned_data.get('password_confirm')
        pw_current = cleaned_data.get('password_current')

        if pw_new or pw_confirm:
            if pw_new != pw_confirm:
                self.add_error('password_confirm', 'New passwords do not match.')
            if not pw_current:
                self.add_error('password_current', 'Please enter your current password to change your password.')

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'birthday', 'website', 'phone', 'location',
                  'receive_offers', 'subscribe_newsletter',
                  'social_facebook', 'social_twitter', 'social_instagram']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }
