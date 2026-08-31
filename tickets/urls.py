from django.urls import path
from .views import ticket_create_view, ticket_list_view

urlpatterns = [
    path('tickets/create/', ticket_create_view, name='ticket-create'),
    path('tickets/', ticket_list_view, name='ticket-list')
]
