from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import TicketCreationForm, TicketChangeForm
from .permissions import get_visible_tickets, can_change_ticket

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
  tickets = get_visible_tickets(request.user)
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
