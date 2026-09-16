from django.contrib.auth.forms import (
    UserCreationForm as BaseUserCreationForm,
    UserChangeForm as BaseUserChangeForm,
)
from django import forms
from .models import User
from .utils import normalize_russian_phone

class UserCreationForm(BaseUserCreationForm):
  class Meta:
    model = User
    fields = (
      'email',
      'first_name',
      'last_name',
      'phone_number',
      'photo',
    )

  def clean_phone_number(self):
      return normalize_russian_phone(
          self.cleaned_data['phone_number']
      )

class UserChangeForm(BaseUserChangeForm):
  class Meta:
    model = User
    fields = (
      'email',
      'first_name',
      'last_name',
      'phone_number',
      'photo'
    )

class ProfileChangeForm(forms.ModelForm):
  class Meta:
    model = User
    fields = (
      'first_name',
      'last_name',
      'phone_number',
      'photo'
    )

  def clean_phone_number(self):
      return normalize_russian_phone(
          self.cleaned_data['phone_number']
      )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field_name in self.fields:
      self.fields[field_name].widget.attrs.update({'class':'form-control'})

    self.fields['first_name'].label = 'Имя'
    self.fields['last_name'].label = 'Фамилия'
    self.fields['phone_number'].label = 'Номер телефона'
    self.fields['photo'].label = 'Фото'

class LoginForm(forms.Form):
  email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ivanov@example.com'}))
  password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['password'].label = 'Пароль'

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

  def clean_phone_number(self):
      return normalize_russian_phone(
          self.cleaned_data['phone_number']
      )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field_name in self.fields:
      self.fields[field_name].widget.attrs.update({'class':'form-control'})

    self.fields['first_name'].label = 'Имя'
    self.fields['last_name'].label = 'Фамилия'
    self.fields['phone_number'].label = 'Номер телефона'
    self.fields['password1'].label = 'Пароль'
    self.fields['password2'].label = 'Подтвердите пароль'

    self.fields['password1'].help_text = """
<ul>
    <li>Минимум 8 символов.</li>
    <li>Не должен быть слишком простым и распространённым.</li>
    <li>Не может состоять только из цифр.</li>
</ul>
"""
    self.fields['password2'].help_text = ''
