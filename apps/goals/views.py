from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django import forms
from .models import Goal


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ('title', 'description', 'category', 'status', 'deadline', 'why', 'reward')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Maqsad nomi...'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'deadline': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'why': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Nima uchun bu muhim...'}),
            'reward': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'O\'zingizni qanday mukofotlaysiz?'}),
        }


@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user)
    
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    
    if status_filter:
        goals = goals.filter(status=status_filter)
    if category_filter:
        goals = goals.filter(category=category_filter)
    
    context = {
        'goals': goals,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'status_choices': Goal.STATUS_CHOICES,
        'category_choices': Goal.CATEGORY_CHOICES,
    }

def _is_ajax(request):
    return (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    )


@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user)
    
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    
    if status_filter:
        goals = goals.filter(status=status_filter)
    if category_filter:
        goals = goals.filter(category=category_filter)
    
    context = {
        'goals': goals,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'status_choices': Goal.STATUS_CHOICES,
        'category_choices': Goal.CATEGORY_CHOICES,
    }

    if _is_ajax(request):
        return JsonResponse({
            'success': True,
            'list_html': render_to_string('goals/_goal_list_partial.html', context, request=request)
        })

    return render(request, 'goals/goal_list.html', context)


@login_required
def goal_detail(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    tasks = goal.tasks.all().order_by('status', '-created_at')
    return render(request, 'goals/goal_detail.html', {'goal': goal, 'tasks': tasks})


@login_required
def goal_detail_partials(request, pk):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    tasks = goal.tasks.all().order_by('status', '-created_at')
    
    context = {'goal': goal, 'tasks': tasks}
    return JsonResponse({
        'success': True,
        'info_html': render_to_string('goals/_goal_info_partial.html', context, request=request),
        'tasks_html': render_to_string('goals/_goal_tasks_partial.html', context, request=request),
    })


@login_required
def goal_create(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            msg = f"🎯 '{goal.title}' maqsadi yaratildi!"
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': msg})
            messages.success(request, msg)
            return redirect('goal_list')
        else:
            if _is_ajax(request):
                return render(request, 'goals/_goal_form_inner.html', {'form': form, 'action': 'Yaratish'}, status=400)
    else:
        form = GoalForm()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'goals/_goal_form_inner.html', {'form': form, 'action': 'Yaratish'})
    return render(request, 'goals/goal_form.html', {'form': form, 'action': 'Yaratish'})


@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            msg = f"✅ '{goal.title}' yangilandi!"
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': msg})
            messages.success(request, msg)
            return redirect('goal_list')
        else:
            if _is_ajax(request):
                return render(request, 'goals/_goal_form_inner.html', {'form': form, 'goal': goal, 'action': 'Tahrirlash'}, status=400)
    else:
        form = GoalForm(instance=goal)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'goals/_goal_form_inner.html', {'form': form, 'goal': goal, 'action': 'Tahrirlash'})
    return render(request, 'goals/goal_form.html', {'form': form, 'goal': goal, 'action': 'Tahrirlash'})


@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        title = goal.title
        goal.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f"🗑️ '{title}' o'chirildi."})
        messages.success(request, f"🗑️ '{title}' o'chirildi.")
        return redirect('goal_list')
    return render(request, 'goals/goal_confirm_delete.html', {'goal': goal})


@login_required
def goal_update_progress(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        progress = int(request.POST.get('progress', 0))
        goal.progress = max(0, min(100, progress))
        if goal.progress == 100:
            goal.status = 'completed'
        elif goal.progress > 0:
            goal.status = 'in_progress'
        goal.save()
        msg = f"Progress yangilandi: {goal.progress}%"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': msg, 'progress': goal.progress})
        messages.success(request, msg)
    return redirect('goal_detail', pk=pk)
