from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import timedelta
from apps.tasks.models import Task
from apps.goals.models import Goal


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _build_dashboard_context(user):
    from django.utils import timezone
    today = timezone.localdate()

    from django.db.models import Q
    today_tasks = Task.objects.filter(
        user=user
    ).filter(
        Q(due_date=today) | 
        Q(due_date__lt=today, status__in=['pending', 'in_progress'])
    ).order_by('status', 'priority', 'due_time', 'due_date')

    upcoming_tasks = Task.objects.filter(
        user=user,
        due_date__gt=today,
        due_date__lte=today + timedelta(days=7),
        status__in=['pending', 'in_progress']
    ).order_by('due_date')[:5]

    overdue_tasks = Task.objects.filter(
        user=user,
        due_date__lt=today,
        status__in=['pending', 'in_progress']
    ).count()

    active_goals = Goal.objects.filter(
        user=user,
        status__in=['pending', 'in_progress']
    ).order_by('deadline')[:4]

    stats = {
        'total_tasks': Task.objects.filter(user=user).count(),
        'completed_tasks': Task.objects.filter(user=user, status='completed').count(),
        'pending_tasks': Task.objects.filter(user=user, status='pending').count(),
        'overdue_tasks': overdue_tasks,
        'total_goals': Goal.objects.filter(user=user).count(),
        'completed_goals': Goal.objects.filter(user=user, status='completed').count(),
    }

    if stats['total_tasks'] > 0:
        stats['completion_rate'] = round((stats['completed_tasks'] / stats['total_tasks']) * 100)
    else:
        stats['completion_rate'] = 0

    return {
        'today_tasks': today_tasks,
        'upcoming_tasks': upcoming_tasks,
        'active_goals': active_goals,
        'stats': stats,
        'today': today,
    }


@login_required
def dashboard_view(request):
    context = _build_dashboard_context(request.user)
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def dashboard_partials(request):
    if not _is_ajax(request):
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    context = _build_dashboard_context(request.user)
    return JsonResponse({
        'success': True,
        'stats_html': render_to_string('dashboard/_stats.html', context, request=request),
        'today_tasks_html': render_to_string('dashboard/_today_tasks.html', context, request=request),
        'upcoming_html': render_to_string('dashboard/_upcoming_tasks.html', context, request=request),
    })
