from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import TruncDate, TruncHour
from django.http import HttpResponseForbidden
from django.db.models import Count, Q, F
from tickets.permissions import get_visible_tickets
from dashboard.permissions import can_visible_dashboard_and_statistics
from tickets.models import Ticket, Category, Priority, Status

# Create your views here.
@login_required
def dashboard_view(request):
    if not can_visible_dashboard_and_statistics(request.user):
        return HttpResponseForbidden('У вас нет разрешения на просмотр этого ресурса.')
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

def get_chart_data(period):
    now = timezone.localtime()

    if period == '7d':
        start = (now - timedelta(days=6)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        end = start + timedelta(days=7)

        queryset = (
            Ticket.objects
            .filter(created_at__gte=start, created_at__lt=end)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        counts = {
            item['date']: item['count']
            for item in queryset
        }

        chart_data = {}

        for i in range(7):
            current_date = (start + timedelta(days=i)).date()
            chart_data[current_date.strftime('%d.%m')] = counts.get(
                current_date,
                0,
            )

        return chart_data

    if period == '30d':
        start = (now - timedelta(days=29)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        end = start + timedelta(days=30)

        queryset = (
            Ticket.objects
            .filter(created_at__gte=start, created_at__lt=end)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        counts = {
            item['date']: item['count']
            for item in queryset
        }

        chart_data = {}

        for i in range(30):
            current_date = (start + timedelta(days=i)).date()
            chart_data[current_date.strftime('%d.%m')] = counts.get(
                current_date,
                0,
            )

        return chart_data

    # today
    start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    end = start + timedelta(days=1)

    queryset = (
        Ticket.objects
        .filter(created_at__gte=start, created_at__lt=end)
        .annotate(hour=TruncHour('created_at'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )

    counts = {
        item['hour'].hour: item['count']
        for item in queryset
    }

    chart_data = {
        f'{hour:02d}:00': counts.get(hour, 0)
        for hour in range(24)
    }

    return chart_data

@login_required
def statistics_view(request):
    if not can_visible_dashboard_and_statistics(request.user):
        return HttpResponseForbidden('У вас нет разрешения на просмотр этого ресурса.')

    period = request.GET.get('period', 'today')

    if period not in ('today', '7d', '30d'):
        period = 'today'

    stats = Ticket.objects.aggregate(
        total = Count('id'),

        new = Count('id', filter=Q(status='new')),
        in_progress = Count('id', filter=Q(status='in progress')),
        resolved = Count('id', filter=Q(status='resolved')),
        closed = Count('id', filter=Q(status='closed')),

        low = Count('id', filter=Q(priority='low')),
        medium = Count('id', filter=Q(priority='medium')),
        high = Count('id', filter=Q(priority='high')),
        critical = Count('id', filter=Q(priority='critical')),

        assigned = Count('id', filter=Q(support__isnull=False)),
        unassigned = Count('id', filter=Q(support__isnull=True)),
    )
    total_tickets = stats['total'] or 1
    category_queryset = (
        Ticket.objects.filter(category__isnull=False).annotate(category_title=F('category__title'))
        .values('category_title')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    category_stats = {
        item['category_title']: {
            'count': item['count'],
            'percentage': round((item['count'] / total_tickets) * 100, 1)
        }
        for item in category_queryset
    }

    chart_data = get_chart_data(period)

    context = {
        'total': stats['total'],

        'new': stats['new'],
        'in_progress': stats['in_progress'],
        'resolved': stats['resolved'],
        'closed': stats['closed'],

        'low': stats['low'],
        'medium': stats['medium'],
        'high': stats['high'],
        'critical': stats['critical'],

        'assigned': stats['assigned'],
        'unassigned': stats['unassigned'],

        'category_stats': category_stats,

        'period': period,
        'chart_data': chart_data
    }
    return render(request, 'dashboard/statistics.html', context=context)
