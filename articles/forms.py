import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm

from articles.models import CATEGORY_CHOICES, TAG_CHOICES, Article, Profile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[('journalist', 'Journalist'), ('editor', 'Editor'), ('admin', 'Admin')])

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(user=user, role=self.cleaned_data['role'])
        return user


class ArticlePage1Form(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Title'}),
    )
    subtitle = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Subtitle'}),
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Article Content'}),
    )
    author_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Author Name'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}),
    )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise ValidationError(_('Title must be at least 10 characters long.'))
        return title

class ArticlePage2Form(forms.Form):
    image = forms.ImageField(required=False)
    tags = forms.MultipleChoiceField(
        choices=TAG_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=True,
    )
    publish_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    agree_terms = forms.BooleanField(
        required=True,
        label='I agree to the terms and conditions.',
    )

    def clean_publish_date(self):
        publish_date = self.cleaned_data.get('publish_date')
        if publish_date <= datetime.date.today():
            raise ValidationError(_('Publish date must be in the future.'))
        return publish_date
    
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'subtitle', 'content', 'category', 'tags', 'publish_date', 'image']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']  # Fields to edit in profile

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['password']