from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from tickets.permissions import get_visible_tickets
from tickets.models import Ticket, Category, Priority, Status

# Create your views here.
@login_required
def dashboard_view(request):
    tickets = get_visible_tickets(request.user)

    search = request.GET.get('search', '')
    category = request.GET.get('category')
    priority = request.GET.get('priority')
    status = request.GET.get('status')
    date_from_raw = request.GET.get('date_from')
    date_to_raw = request.GET.get('date_to')

    raw_filters = {
        'category_id': category,
        'priority': priority,
        'status': status,
    }

    active_filters = {k: v for k, v in raw_filters.items() if v}

    if search:
        tickets = tickets.filter(title__icontains=search)

    if active_filters:
        tickets = tickets.filter(**active_filters)

    if date_from_raw:
        try:
            date_from = datetime.strptime(
                date_from_raw,
                '%Y-%m-%d'
            ).date()

            date_from = timezone.make_aware(
                datetime.combine(date_from, datetime.min.time())
            )

            tickets = tickets.filter(created_at__gte=date_from)
        except ValueError:
            pass

    if date_to_raw:
        try:
            date_to = datetime.strptime(
                date_to_raw,
                '%Y-%m-%d'
            ).date()

            date_to = date_to + timedelta(days=1)

            date_to = timezone.make_aware(
                datetime.combine(date_to, datetime.min.time())
            )

            tickets = tickets.filter(created_at__lt=date_to)
        except ValueError:
            pass

    tickets = tickets.order_by('-created_at')

    context = {
        'tickets': tickets,
        'search': search,
        'categories': Category.objects.all(),
        'priorities': Priority.choices,
        'statuses': Status.choices,

        'current_category': category,
        'current_priority': priority,
        'current_status': status,

        'date_from': date_from_raw,
        'date_to': date_to_raw
    }

    return render(request, 'dashboard/dashboard.html', context)
