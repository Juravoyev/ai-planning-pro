from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import date, timedelta
from .models import Habit, HabitCompletion


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _build_habits_context(user):
    habits = Habit.objects.filter(user=user)
    today = date.today()

    habits_data = []
    for h in habits:
        completed_dates = h.get_completed_dates()
        last7 = h.get_last7_dates()
        day_names = ['Ya', 'Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh']

        days_info = []
        for d in last7:
            days_info.append({
                'date': d,
                'date_str': d.isoformat(),
                'day_name': day_names[d.weekday() if d.weekday() < 6 else 6],
                'done': d in completed_dates,
                'is_today': d == today,
            })

        last30 = set((today - timedelta(days=i)) for i in range(30))
        done_last30 = len(completed_dates & last30)

        habits_data.append({
            'habit': h,
            'days': days_info,
            'done_today': today in completed_dates,
            'done_last30': done_last30,
            'completion_rate': round((done_last30 / 30) * 100),
        })

    total = habits.count()
    done_today_count = sum(1 for h in habits_data if h['done_today'])

    return {
        'habits_data': habits_data,
        'today': today,
        'total': total,
        'done_today': done_today_count,
        'emoji_list': ['💪','📚','🏃','💧','🧘','🍎','✍️','🎯','😴','🎵','🌅','🚴','🏋️','📝','🎨'],
    }


@login_required
def habits_view(request):
    context = _build_habits_context(request.user)
    return render(request, 'habits/habits.html', context)


@login_required
def habits_partials(request):
    if not _is_ajax(request):
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    context = _build_habits_context(request.user)
    return JsonResponse({
        'success': True,
        'stats_html': render_to_string('habits/_habits_stats.html', context, request=request),
        'list_html': render_to_string('habits/_habits_list.html', context, request=request),
    })


@login_required
@require_POST
def habit_create(request):
    name = request.POST.get('name', '').strip()
    icon = request.POST.get('icon', '💪').strip() or '💪'
    if name:
        Habit.objects.create(user=request.user, name=name, icon=icon)
        if _is_ajax(request):
            return JsonResponse({'success': True, 'message': "✅ '" + name + "' odati qo'shildi!"})
        messages.success(request, "✅ '" + name + "' odati qo'shildi!")
        return redirect('habits')

    if _is_ajax(request):
        return JsonResponse({'success': False, 'error': 'Odat nomi bo‘sh bo‘lishi mumkin emas.'}, status=400)
    return redirect('habits')


@login_required
@require_POST
def habit_toggle(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    date_str = request.POST.get('date', date.today().isoformat())

    try:
        toggle_date = date.fromisoformat(date_str)
    except ValueError:
        toggle_date = date.today()

    completion, created = HabitCompletion.objects.get_or_create(
        habit=habit, date=toggle_date
    )
    if not created:
        completion.delete()
        done = False
    else:
        done = True

    habit.recalc_streak()
    return JsonResponse({'success': True, 'done': done, 'streak': habit.streak})


@login_required
@require_POST
def habit_delete(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    name = habit.name
    habit.delete()
    if _is_ajax(request):
        return JsonResponse({'success': True, 'message': "🗑️ '" + name + "' o'chirildi."})
    messages.success(request, "🗑️ '" + name + "' o'chirildi.")
    return redirect('habits')
