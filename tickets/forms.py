from django.forms import ModelForm
from .models import Ticket

class TicketCreationForm(ModelForm):
  class Meta:
    model = Ticket
    fields = (
      'title',
      'category',
      'description',
    )

class TicketChangeForm(ModelForm):
  class Meta:
    model = Ticket
    fields = (
      'title',
      'category',
      'description',
      'priority',
      'status',
      'support'
    )
