from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import (
    TicketSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .filters import TicketFilter
from .forms import TicketCreationForm, TicketChangeForm
from .permissions import get_visible_tickets, can_change_ticket, CanChangeTicketPermission

# Create your views here.
@login_required
def ticket_create_view(request):
  if request.method == 'POST':
    form = TicketCreationForm(request.POST)
    if form.is_valid():
      ticket = form.save(commit=False)
      ticket.user = request.user
      ticket.save()

      return redirect('ticket-list')

  else:
    form = TicketCreationForm()

  return render(request, 'tickets/create.html', {'form': form})

@login_required
def ticket_list_view(request):
  if not request.user.has_perm('tickets.view_ticket'):
    return HttpResponseForbidden('У вас нет разрешения на просмотр этого ресурса.')
  tickets = get_visible_tickets(request.user).order_by('-created_at')
  return render(request, 'tickets/list.html', {'tickets': tickets})

@login_required
def ticket_detail_view(request, pk):
  if not request.user.has_perm('tickets.view_ticket'):
      return HttpResponseForbidden('У вас нет разрешения на просмотр этого ресурса.')
  tickets = get_visible_tickets(request.user)
  ticket = get_object_or_404(tickets, pk=pk)
  return render(request, 'tickets/detail.html', {'ticket': ticket})

@login_required
def ticket_change_view(request, pk):
  tickets = get_visible_tickets(request.user)
  ticket = get_object_or_404(tickets, pk=pk)
  if request.method == 'POST':
    if not request.user.has_perm('tickets.change_ticket'):
      return HttpResponseForbidden('У вас нет разрешения на изменение этого ресурса.')
    if not can_change_ticket(request.user, ticket):
      return HttpResponseForbidden('У вас нет разрешения на изменение этого ресурса.')
    form = TicketChangeForm(request.POST, user=request.user, instance=ticket)
    if form.is_valid():
      ticket = form.save()
      return redirect('ticket-detail', pk=ticket.pk)
  else:
    form = TicketChangeForm(instance=ticket, user=request.user)
  return render(request, 'tickets/change.html', {'ticket': ticket, 'form': form})

@extend_schema_view(
    create=extend_schema(request=TicketCreateSerializer),
    update=extend_schema(request=TicketUpdateSerializer),
    partial_update=extend_schema(request=TicketUpdateSerializer),
)
class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
  ):

  serializer_class = TicketSerializer

  filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
  filterset_class = TicketFilter
  search_fields = ['title', 'description']
  ordering_fields = ['category', 'priority', 'status', 'created_at']
  ordering = ['-created_at']

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)

  def get_queryset(self):
      queryset = get_visible_tickets(self.request.user)

      return queryset

  def get_permissions(self):
    if self.action in ['list', 'create', 'retrieve']:
      return [IsAuthenticated()]
    else:
      return [IsAuthenticated(), CanChangeTicketPermission()]

