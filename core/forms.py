import os
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile

ALLOWED_AVATAR_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', max_length=150)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise ValidationError('Неверный логин или пароль.')
        return cleaned_data

    def get_user(self):
        return self.user_cache


class SignUpForm(forms.ModelForm):
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='Имя', max_length=150, required=True)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Этот email уже зарегистрирован.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Проверка через AUTH_PASSWORD_VALIDATORS из settings.py
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Пароли не совпадают.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Profile.objects.create(user=user)
        return user


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='Никнейм / Имя', max_length=150, required=True)
    avatar = forms.ImageField(label='Аватар', required=False)

    class Meta:
        model = Profile
        fields = ('avatar',)

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['first_name'].initial = self.user.first_name

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError('Этот email уже используется другим пользователем.')
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in ALLOWED_AVATAR_EXTENSIONS:
                raise ValidationError(f'Допустимые форматы: {", ".join(ALLOWED_AVATAR_EXTENSIONS)}.')
            if avatar.size > MAX_AVATAR_SIZE:
                raise ValidationError('Размер файла не должен превышать 2 МБ.')
        return avatar

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.email = self.cleaned_data['email']
        self.user.first_name = self.cleaned_data['first_name']
        if commit:
            self.user.save()
            profile.save()
        return profile