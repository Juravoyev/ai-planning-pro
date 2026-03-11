from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from apps.tasks.models import Task
from apps.goals.models import Goal


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.username}! 🎉")
            return redirect('dashboard')
        else:
            messages.error(request, "Xatolik yuz berdi. Iltimos qayta urinib ko'ring.")
    else:
        form = RegisterForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Qaytib keldingiz, {user.username}! 👋")
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        messages.error(request, "Email yoki parol noto'g'ri.")
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect('login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil yangilandi! ✅")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    # Statistika
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, status='completed').count()
    total_goals = Goal.objects.filter(user=request.user).count()
    completed_goals = Goal.objects.filter(user=request.user, status='completed').count()
    
    context = {
        'form': form,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
    }
    return render(request, 'users/profile.html', context)
