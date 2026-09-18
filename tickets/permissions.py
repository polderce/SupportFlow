from django.db.models import QuerySet, Q
from rest_framework import viewsets
from rest_framework.permissions import BasePermission
from .models import Ticket, Status


def get_visible_tickets(user) -> QuerySet[Ticket]:
    if user.is_superuser:
        return Ticket.objects.all()

    if user.groups.filter(name='Manager').exists():
        return Ticket.objects.all()

    if user.groups.filter(name='Support').exists():
        return Ticket.objects.filter(Q(support=user) | Q(user=user))

    if user.groups.filter(name='User').exists():
        return Ticket.objects.filter(user=user)
    return Ticket.objects.none()

def can_change_ticket(user, ticket):
    if user.is_superuser:
        return True

    if user.groups.filter(name='Manager').exists():
        return True

    if user.groups.filter(name='Support').exists():
        if ticket.support == user:
            return True

    return False

def can_edit_basic_fields(user, instance):
    if user.groups.filter(name='Manager').exists() or user.is_superuser:
      return True
    return instance.support == user and (instance.status != Status.RESOLVED and instance.status != Status.CLOSED)

class CanChangeTicketPermission(BasePermission):
    def has_object_permission(self, request, view, obj):

        return can_change_ticket(request.user, obj)


