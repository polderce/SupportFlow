from django.urls import path
from .views import login_view, logout_view, register_view, profile_view, profile_change_view

urlpatterns = [
  path('users/login/', login_view, name='login'),
  path('users/logout/', logout_view, name='logout'),
  path('users/register/', register_view, name='register'),
  path('users/profile/<int:pk>/', profile_view, name='profile'),
  path('users/profile/<int:pk>/change/', profile_change_view, name='profile-change')
]
