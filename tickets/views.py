from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TicketCreationForm

# Create your views here.
@login_required
def ticket_view(request):
  if request.method == 'POST':
    form = TicketCreationForm(request.POST)
    if form.is_valid():
      ticket = form.save(commit=False)
      ticket.user = request.user
      ticket.save()

      return redirect('ticket')

  else:
    form = TicketCreationForm()

  return render(request, 'ticket.html', {'form': form})


