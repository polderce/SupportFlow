from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import TicketCreationForm
from .models import Ticket

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
  if request.user.has_perm('tickets.view_ticket'):
    if request.user.groups.filter(name='User').exists():
      tickets = Ticket.objects.filter(user=request.user)
    elif request.user.groups.filter(name='Support').exists() or request.user.groups.filter(name='Manager').exists():
      tickets = Ticket.objects.all()
    else:
      return HttpResponseForbidden('У вас нет разрешения на просмотр этого ресурса.')
    return render(request, 'tickets/list.html', {'tickets': tickets})
  else:
    return HttpResponseForbidden('У вас нет разрешения на просмотр этого ресурса.')

@login_required
def ticket_detail_view(request, pk):
  if not request.user.has_perm('tickets.view_ticket'):
    return HttpResponseForbidden('У вас нет разрешения на просмотр этого ресурса.')
  ticket = get_object_or_404(Ticket, pk=pk)
  if request.user.groups.filter(name='User').exists():
    if ticket.user != request.user:
      return HttpResponseForbidden('У вас нет разрешения на просмотр этого ресурса.')
  elif not (request.user.groups.filter(name='Support').exists() or request.user.groups.filter(name='Manager').exists()):
    return HttpResponseForbidden('У вас нет разрешения на просмотр этого ресурса.')
  return render(request, 'tickets/detail.html', {'ticket': ticket})
