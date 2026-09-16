from django.urls import path
from .views import dashboard_view, statistics_view

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('statistics/', statistics_view, name='statistics')
]

