from django.urls import path
from .views import ticket_view

urlpatterns = [
    path('ticket/', ticket_view, name='ticket')
]
