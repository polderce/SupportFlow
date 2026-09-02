from django.urls import path
from .views import ticket_create_view, ticket_list_view, ticket_detail_view, ticket_change_view

urlpatterns = [
    path('tickets/create/', ticket_create_view, name='ticket-create'),
    path('tickets/', ticket_list_view, name='ticket-list'),
    path('tickets/<int:pk>/', ticket_detail_view, name='ticket-detail'),
    path('tickets/<int:pk>/change/', ticket_change_view, name='ticket-change')
]
