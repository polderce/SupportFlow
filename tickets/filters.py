import django_filters
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Ticket


class TicketFilter(django_filters.FilterSet):

    date_from = django_filters.DateFilter(method='filter_date_from')
    date_to = django_filters.DateFilter(method='filter_date_to')

    def filter_date_from(self, queryset, name, value):
        date_from = timezone.make_aware(
            datetime.combine(value, datetime.min.time())
        )
        return queryset.filter(created_at__gte=date_from)

    def filter_date_to(self, queryset, name, value):
        date_to = value + timedelta(days=1)
        date_to = timezone.make_aware(
            datetime.combine(date_to, datetime.min.time())
        )
        return queryset.filter(created_at__lt=date_to)

    class Meta:
        model = Ticket
        fields = ['category', 'priority', 'status']
