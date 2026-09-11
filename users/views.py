from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from .forms import LoginForm, RegisterForm

# Create your views here.
def login_view(request):
    if request.method == 'POST':
      form = LoginForm(request.POST)
      if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('ticket-list')
        else:
            form.add_error(None, ValidationError('Неверный email или пароль', code='invalid_login'))
    else:
      form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
  logout(request)
  return redirect('login')

def register_view(request):
  if request.method == 'POST':
    form = RegisterForm(request.POST)
    if form.is_valid():
        user = form.save()
        group = Group.objects.get(name='User')
        user.groups.add(group)
        return redirect('login')
  else:
     form = RegisterForm()
  return render(request, 'users/register.html', {'form': form})
