from django.db.models import QuerySet

from .models import Ticket


def get_visible_tickets(user) -> QuerySet[Ticket]:
    if user.is_superuser:
        return Ticket.objects.all()

    if user.groups.filter(name__in=['Support', 'Manager']).exists():
        return Ticket.objects.all()

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
