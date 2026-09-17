from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from .forms import LoginForm, RegisterForm, ProfileChangeForm
from .permissions import can_access_profile

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

User = get_user_model()

@login_required
def profile_view(request, pk):
  target_user = get_object_or_404(User, pk=pk)

  if not can_access_profile(request.user, target_user):
    return HttpResponseForbidden("У вас нет доступа к этому профилю.")
  return render(request, 'users/profile.html', {'profile_user':target_user})

@login_required
def profile_change_view(request, pk):
  target_user = get_object_or_404(User, pk=pk)

  if not can_access_profile(request.user, target_user):
    return HttpResponseForbidden("У вас нет доступа к этому профилю.")

  if request.method == 'POST':
    form = ProfileChangeForm(request.POST, request.FILES, instance=target_user)
    if form.is_valid():
       form.save()
       return redirect('profile', pk=pk)
  else:
    form = ProfileChangeForm(instance=target_user)
  return render(request, 'users/profile_change.html', {'profile_user':target_user, 'form':form})

