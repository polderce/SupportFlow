from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import Ticket, Status
from users.models import User

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

  def can_edit_basic_fields(self):
    if self.user.groups.filter(name='Manager').exists():
      return True
    return self.instance.support == self.user and (self.instance.status != Status.RESOLVED and self.instance.status != Status.CLOSED)



  def __init__(self, *args, user, **kwargs):
    self.user = user
    super().__init__(*args, **kwargs)
    self.fields['support'].queryset = User.objects.filter(groups__name='Support')
    if user.groups.filter(name='Support').exists():
      if not self.can_edit_basic_fields():
        self.fields['title'].widget.attrs['disabled'] = True
        self.fields['description'].widget.attrs['disabled'] = True
        self.fields['category'].widget.attrs['disabled'] = True
        self.fields['support'].widget.attrs['disabled'] = True

  def clean(self):
    cleaned_data = super().clean()

    protected_fields = ['title', 'description', 'category', 'support']
    if not self.can_edit_basic_fields():
      for field_name in protected_fields:
        original_value = getattr(self.instance, field_name)
        user_value = cleaned_data.get(field_name)

        if original_value != user_value:
          raise ValidationError(f"Поле '{field_name}' нельзя менять. Оно защищено.")

    return cleaned_data




