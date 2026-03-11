from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date, timedelta


@login_required
def analytics_view(request):
    user = request.user
    today = date.today()

    # --- TASKS ---
    try:
        from apps.tasks.models import Task
        tasks = Task.objects.filter(user=user)
        total_tasks = tasks.count()
        done_tasks = tasks.filter(status='completed').count()
        pending_tasks = total_tasks - done_tasks
        completion_pct = round((done_tasks / total_tasks * 100)) if total_tasks else 0
        remaining_pct = 100 - completion_pct

        # Kategoriyalar
        cat_data = [
            {'key': 'work',     'label': '💼 Ish',     'color': '#6C63FF'},
            {'key': 'study',    'label': '📚 Ta\'lim', 'color': '#9b5de5'},
            {'key': 'personal', 'label': '❤️ Shaxsiy', 'color': '#f72585'},
            {'key': 'health',   'label': '💪 Sog\'liq', 'color': '#06d6a0'},
        ]
        categories = []
        for c in cat_data:
            count = tasks.filter(category=c['key']).count()
            categories.append({
                'label': c['label'],
                'color': c['color'],
                'count': count,
                'pct': round(count / total_tasks * 100) if total_tasks else 0,
            })

        # Ustuvorlik
        prio_data = [
            {'key': 'urgent', 'label': '🔴 Shoshilinch', 'color': '#E74C3C'},
            {'key': 'high',   'label': '🟠 Yuqori',      'color': '#E67E22'},
            {'key': 'medium', 'label': '🟡 O\'rta',      'color': '#F39C12'},
            {'key': 'low',    'label': '🟢 Past',         'color': '#27AE60'},
        ]
        priorities = []
        for p in prio_data:
            count = tasks.filter(priority=p['key']).count()
            priorities.append({
                'label': p['label'],
                'color': p['color'],
                'count': count,
                'pct': round(count / total_tasks * 100) if total_tasks else 0,
            })

        # Oxirgi 7 kun
        weekly_activity = []
        day_names = ['Ya', 'Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh']
        counts = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            count = tasks.filter(due_date=d).count()
            counts.append(count)

        max_count = max(counts) if any(counts) else 1
        for i, c in enumerate(counts):
            d = today - timedelta(days=6 - i)
            weekly_activity.append({
                'date': d.strftime('%d/%m'),
                'name': day_names[d.weekday() if d.weekday() < 7 else 0],
                'count': c,
                'height': max(8, round(c / max_count * 80)) if max_count else 8,
            })

    except Exception:
        total_tasks = done_tasks = pending_tasks = completion_pct = 0
        remaining_pct = 100
        categories = []
        priorities = []
        weekly_activity = []

    # --- GOALS ---
    try:
        from apps.goals.models import Goal
        goals_qs = Goal.objects.filter(user=user)
        total_goals = goals_qs.count()
        goals = [{'icon': g.icon, 'title': g.title, 'progress': g.progress} for g in goals_qs[:6]]
    except Exception:
        total_goals = 0
        goals = []

    # --- HABITS ---
    try:
        from apps.habits.models import Habit
        habits_qs = Habit.objects.filter(user=user)
        last30 = set((today - timedelta(days=i)) for i in range(30))
        habits_stats = []
        for h in habits_qs:
            completed = h.get_completed_dates()
            done = len(completed & last30)
            habits_stats.append({
                'icon': h.icon,
                'name': h.name,
                'streak': h.streak,
                'done': done,
                'rate': round(done / 30 * 100),
            })
    except Exception:
        habits_stats = []

    context = {
        'total_tasks': total_tasks,
        'done_tasks': done_tasks,
        'pending_tasks': pending_tasks,
        'completion_pct': completion_pct,
        'remaining_pct': remaining_pct,
        'total_goals': total_goals,
        'categories': categories,
        'priorities': priorities,
        'weekly_activity': weekly_activity,
        'goals': goals,
        'habits_stats': habits_stats,
    }
    return render(request, 'analytics/analytics.html', context)
