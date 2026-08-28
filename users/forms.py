from django.contrib.auth.forms import (
    UserCreationForm as BaseUserCreationForm,
    UserChangeForm as BaseUserChangeForm,
)
from django import forms
from .models import User

class UserCreationForm(BaseUserCreationForm):
  class Meta:
    model = User
    fields = (
      'email',
      'first_name',
      'last_name',
      'phone_number',
      'photo',
      'role'
    )

class UserChangeForm(BaseUserChangeForm):
  class Meta:
    model = User
    fields = (
      'email',
      'first_name',
      'last_name',
      'phone_number',
      'photo',
      'role'
    )

class LoginForm(forms.Form):
  email = forms.EmailField()
  password = forms.CharField(widget=forms.PasswordInput)

class RegisterForm(UserCreationForm):
  email = forms.EmailField()
  class Meta:
    model = User
    fields = (
      'email',
      'first_name',
      'last_name',
      'phone_number',
      'password1',
      'password2'
    )

