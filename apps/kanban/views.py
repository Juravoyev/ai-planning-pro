from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from apps.tasks.models import Task


@login_required
def kanban_board(request):
    user = request.user

    columns = {
        'pending': {
            'title': 'Yangi',
            'icon': '📋',
            'color': '#6C63FF',
            'tasks': Task.objects.filter(user=user, status='pending').order_by('-created_at')
        },
        'in_progress': {
            'title': 'Jarayonda',
            'icon': '🔄',
            'color': '#F39C12',
            'tasks': Task.objects.filter(user=user, status='in_progress').order_by('-created_at')
        },
        'completed': {
            'title': 'Bajarildi',
            'icon': '✅',
            'color': '#27AE60',
            'tasks': Task.objects.filter(user=user, status='completed').order_by('-created_at')
        },
        'cancelled': {
            'title': 'Bekor qilindi',
            'icon': '❌',
            'color': '#E74C3C',
            'tasks': Task.objects.filter(user=user, status='cancelled').order_by('-created_at')
        },
    }

    context = {'columns': columns}
    return render(request, 'kanban/board.html', context)


@login_required
@require_POST
def update_task_status(request):
    """AJAX: Drag & Drop orqali vazifa statusini yangilash"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('status')

        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if not task_id:
            return JsonResponse({'success': False, 'error': "task_id yo'q"}, status=400)
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': "Noto'g'ri status"})

        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.status = new_status

        if new_status == 'completed':
            from django.utils import timezone
            task.completed_at = timezone.now()
        else:
            task.completed_at = None

        task.save()
        return JsonResponse({'success': True, 'status': new_status})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
