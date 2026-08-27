from django.db import models
from users.models import User

# Create your models here.
class Status(models.TextChoices):
  NEW = 'new', 'Новый'
  IN_PROGRESS = 'in progress', 'В работе'
  RESOLVED = 'resolved', 'Решен'
  CLOSED = 'closed', 'Закрыт'

class Priority(models.TextChoices):
  LOW = 'low', 'Низкий'
  MEDIUM = 'medium', 'Средний'
  HIGH = 'high', 'Высокий'
  CRITICAL = 'critical', 'Критический'

class Category(models.Model):
  title = models.CharField(max_length=50)
  description = models.TextField()

  def __str__(self):
    return self.title

class Ticket(models.Model):
  user = models.ForeignKey(User, related_name='created_tickets', on_delete=models.PROTECT)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  title = models.CharField(max_length=50)
  category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True)
  description = models.TextField()
  priority = models.CharField(max_length=15, choices=Priority.choices, default=Priority.LOW)
  status = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW)
  support = models.ForeignKey(User, related_name='assigned_tickets', on_delete=models.PROTECT, blank=True, null=True)

