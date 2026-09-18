from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import Ticket
from users.models import User
from .permissions import can_edit_basic_fields

class TicketCreationForm(ModelForm):
  class Meta:
    model = Ticket
    fields = (
      'title',
      'category',
      'description',
    )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field_name in self.fields:
      self.fields[field_name].widget.attrs.update({'class':'form-control'})

    self.fields['title'].label = 'Заголовок'
    self.fields['category'].label = 'Категория'
    self.fields['description'].label = 'Описание'

    self.fields['category'].empty_label = 'Выберите из списка'
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

  def __init__(self, *args, user, **kwargs):
    self.user = user
    super().__init__(*args, **kwargs)
    self.fields['support'].queryset = User.objects.filter(groups__name='Support')
    if user.groups.filter(name='Support').exists():
      if not can_edit_basic_fields(self.user, self.instance):
        self.fields['title'].disabled = True
        self.fields['description'].disabled = True
        self.fields['category'].disabled = True
        self.fields['priority'].disabled = True
        self.fields['support'].disabled = True

    for field_name in self.fields:
      self.fields[field_name].widget.attrs.update({'class':'form-control'})

    self.fields['title'].label = 'Заголовок'
    self.fields['category'].label = 'Категория'
    self.fields['description'].label = 'Описание'
    self.fields['priority'].label = 'Приоритет'
    self.fields['status'].label = 'Статус'
    self.fields['support'].label = 'Support'

    self.fields['support'].empty_label = 'Выберите из списка'

  def clean(self):
    cleaned_data = super().clean()

    protected_fields = ['title', 'description', 'category', 'priority', 'support']

    if not can_edit_basic_fields(self.user, self.instance):
      for field_name in protected_fields:
        original_value = getattr(self.instance, field_name)
        field_in_cleaned = field_name in cleaned_data
        user_value = cleaned_data.get(field_name)

        if field_in_cleaned and user_value != original_value:
          raise ValidationError(f"Поле '{field_name}' нельзя менять. Оно защищено.")
        else:
          cleaned_data[field_name] = original_value

    return cleaned_data




