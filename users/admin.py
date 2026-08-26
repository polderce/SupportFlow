from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Стандартная админка, на которой мы основываемся
from .models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# Register your models here.
@admin.register(User) # Регистрация нашей кастомной модели User
class CustomUserAdmin(UserAdmin): # Настройка админки
  add_form = UserCreationForm # Создание - кастомная форма
  form = UserChangeForm # Редактирование - кастомная форма

  list_display = (
      'email',
      'first_name',
      'last_name',
      'role',
      'is_staff',
      'is_active'
  )

  ordering = ('email',)

  fieldsets = (
      (None, { # Основные данные
        "fields": (
            'email', 'password',
        ),
      }),
      ('Personal info', { # Кастомные поля
        'fields': (
          'first_name', 'last_name', 'phone_number', 'photo', 'role',
        )
      }),
      ('Permissions', { # Права
        'fields': (
          'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
        )
      }),
  )

  add_fieldsets = (
      (None, {
          'classes': (
            'wide',
            ),
          'fields': (
              'email',
              'first_name',
              'last_name',
              'phone_number',
              'role',
              'password1',
              'password2',
              'is_staff',
              'is_active',
          ),
      }),
  )
