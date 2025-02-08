import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import re
from articles.models import CATEGORY_CHOICES, TAG_CHOICES, Article, Profile

User = get_user_model()
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

# Username validation
    def clean_username(self):
        username = self.cleaned_data.get('username')

        # 1. Check if length is valid (max 8 characters)
        if len(username) > 3:
            raise ValidationError("Username between 3 to 12 character")
        
        # 2. Check if it starts with an alphabet
        if not username[0].isalpha():
            raise ValidationError("Username must start with an alphabet.")
        
        # 3. Check if it contains only allowed special characters (underscore)
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            raise ValidationError("Only alphanumeric characters and underscore (_) are allowed in the username.")

          # Check if it contains at least three alphabets
        alphabet_count = sum(char.isalpha() for char in username)
        if alphabet_count < 3:
            raise ValidationError("Username must contain at least three alphabets.")
        
        return username

    # Email validation (ensure it's unique)
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        
        return email

    # Password validation
    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        # 1. Check for minimum length
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        # 2. Check for at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")

        # 3. Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            raise ValidationError("Password must contain at least one lowercase letter.")

        # 4. Check for at least one special character
        if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in password):
            raise ValidationError("Password must contain at least one special character.")

        return password

    # Confirm Password validation
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Ensure passwords match
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        
        return cleaned_data

class ArticlePage1Form(forms.Form):
    title = forms.CharField(
        max_length=25,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Title'}),
    )
    subtitle = forms.CharField(
        max_length=25,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Subtitle'}),
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Article Content'}),
    )
    author_name = forms.CharField(
        max_length=20,
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
        widget=forms.DateInput(attrs={
            'type': 'date',
            'min': datetime.date.today().isoformat(),  # Set minimum date to today
        }),
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
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role']  # Assuming role is a field in the Profile model
        
# class UserCreationForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         # roles = forms.ChoiceField(choices=[('journalist', 'Journalist'), ('editor', 'Editor'), ('admin', 'Admin')])
#         fields = ['username', 'email', 'password']
