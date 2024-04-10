from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect

from usermanagement.forms import CustomUserCreationForm
from usermanagement.models import CustomUser

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})



@user_passes_test(lambda u: u.is_superuser)
def approve_users(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(pk=user_id)
        user.is_active = True
        user.is_approved = True
        user.save()
        return redirect('approve_users')

    users_to_approve = CustomUser.objects.filter(is_approved=False)
    return render(request, 'approve_users.html', {'users': users_to_approve})
