from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.template.loader import render_to_string
from .models import Task
from .forms import TaskForm


def _is_ajax(request):
    return (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    )


def _build_task_list_context(request):
    tasks = Task.objects.filter(user=request.user)

    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('q', '')

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if category_filter:
        tasks = tasks.filter(category=category_filter)
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    return {
        'tasks': tasks,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'category_choices': Task.CATEGORY_CHOICES,
        'total_count': tasks.count(),
    }


@login_required
def task_list(request):
    context = _build_task_list_context(request)
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_partials(request):
    if not _is_ajax(request):
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    context = _build_task_list_context(request)
    return JsonResponse({
        'success': True,
        'header_html': render_to_string('tasks/_task_header.html', context, request=request),
        'list_html': render_to_string('tasks/_task_list.html', context, request=request),
    })


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            
            if _is_ajax(request):
                return JsonResponse({
                    'success': True, 
                    'message': f"✅ '{task.title}' vazifasi yaratildi!"
                })
            messages.success(request, f"✅ '{task.title}' vazifasi yaratildi!")
            return redirect('task_list')
        else:
            print(f"DEBUG: Task form errors: {form.errors}")
            if _is_ajax(request):
                return render(request, 'tasks/_task_form_inner.html', {'form': form, 'action': 'Yaratish'}, status=400)
    else:
        goal_id = request.GET.get('goal')
        initial = {}
        if goal_id:
            initial['goal'] = goal_id
        form = TaskForm(user=request.user, initial=initial)
    
    if _is_ajax(request):
        return render(request, 'tasks/_task_form_inner.html', {'form': form, 'action': 'Yaratish'})
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Yaratish'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ '{task.title}' yangilandi!")
            if _is_ajax(request):
                return JsonResponse({
                    'success': True, 
                    'message': f"✅ '{task.title}' yangilandi!"
                })
            return redirect('task_list')
        else:
            if _is_ajax(request):
                return render(request, 'tasks/_task_form_inner.html', {'form': form, 'task': task, 'action': 'Tahrirlash'}, status=400)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    if _is_ajax(request):
        return render(request, 'tasks/_task_form_inner.html', {'form': form, 'task': task, 'action': 'Tahrirlash'})
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task, 'action': 'Tahrirlash'})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        title = task.title
        task.delete()
        if _is_ajax(request):
            return JsonResponse({'success': True, 'message': f"🗑️ '{title}' o'chirildi."})
        messages.success(request, f"🗑️ '{title}' o'chirildi.")
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_complete(request, pk):
    """AJAX orqali vazifani holatini (bajarildi/pending) o'zgartirish"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    new_status = task.toggle_completed()
    
    if new_status == 'completed':
        msg = f"🎉 '{task.title}' bajarildi!"
    else:
        msg = f"⏳ '{task.title}' kutish ruyxatiga qaytarildi."

    if _is_ajax(request):
        return JsonResponse({'success': True, 'status': new_status, 'message': msg})
    
    messages.success(request, msg)
    return redirect('task_list')


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'tasks/task_detail.html', {'task': task})
