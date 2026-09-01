from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin # Импорт нужных модулей
# AbstractBaseUser - базовый класс, который служит фундаментом для создания
# кастомной модели пользователя, имеет нужный нам функционал (аунтефикация, хэширование паролей, сброс)
# BaseUserManager - базовый класс для менеджеров, служит кастомной логикой для создания пользователя
# PermissionsMixin - абстрактный базовый класс, который упрощает интеграцию системы разрешений
# фреймворка в кастомную модель (тут как раз появляется is_superuser и is_staff)
from django.db import models

# Create your models here.
class UserManager(BaseUserManager): # Клас создания пользователя и админа
  def create_user(self, email, password, **exstra_fields): # Функция создания пользователя
    if not email: # Если поле пустое, то появляется ошибка
      raise ValueError('Email is required') # raise ValueError - создание исключения, который прерывает текущую функцию,
                                            # текст ошибки
    email = self.normalize_email(email) # normalize_email - нормализация почты, все, что после @ получается нижним регистром
    user = self.model(email=email, **exstra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, email, password, **exstra_fields): # Функция создания суперпользователя
    exstra_fields['is_staff'] = True
    exstra_fields['is_superuser'] = True

    return self.create_user(email, password, **exstra_fields)

class User(AbstractBaseUser, PermissionsMixin): # Класс пользователя с полями
  first_name = models.CharField(max_length=50) # CharFiled - текстовое поле для небольшого объема,
                                                           # max_length - максимальная длина, null - пустое или нет
  last_name = models.CharField(max_length=50)
  email = models.EmailField(unique=True, null=False, blank=False) # EmailField - поле почты,
                                                                  # unique - уникальное/не уникальное,
                                                                  # blank=False - обязательное/не обязательное
  phone_number = models.CharField(max_length=50, blank=False, unique=True) # Правильная запись будет через валидатор в форме
  is_active = models.BooleanField(default=True) # is_active - активен или деактивирован ли аккаунт, BooleanField -
                                                # булево значение (True/False), default - что будет по умолчанию
  is_staff = models.BooleanField(default=False) # is_staff - флаг, который определяет доступ к админке
  photo = models.ImageField(upload_to='photo/', # ImageField - поле для изображения, хранит путь, upload_to - параметры куда загружать
                            blank=True,
                            null=True,
                            verbose_name='Фото') # verbose_name - удобное название для интерфейса
  created_at = models.DateTimeField(auto_now_add=True) # DateTimeField - поле времени, auto_now_add=True - текущее время при создании

  objects = UserManager()

  USERNAME_FIELD = 'email' # атрибут в модели, который указывает, что будет уникальным идентификатором для аунтификации
  REQUIRED_FIELDS = ['first_name', 'last_name'] # атрибут, который указывает, какие поля будут запрашиваться для создания суперпользователя

  def __str__(self):
    return self.email # удобное отображение в консоли/админке

