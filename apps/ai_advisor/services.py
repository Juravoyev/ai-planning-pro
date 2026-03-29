import json as _json
import urllib.request
import urllib.error
from django.utils import timezone
from django.conf import settings


def call_gemini(user_message, system_prompt):
    api_key = settings.GEMINI_API_KEY
    models_to_try = [
        ("gemini-2.0-flash", f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"),
        ("gemini-1.5-flash", f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"),
    ]

    errors = []
    for model_name, url in models_to_try:
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_message}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024},
        }
        data = _json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = _json.loads(resp.read().decode("utf-8"))
                return result["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            try:
                err_data = _json.loads(body)
                error_msg = err_data.get('error', {}).get('message', 'Noma\'lum xato')
            except Exception:
                error_msg = body
            errors.append(f"{model_name}: {error_msg}")
        except urllib.error.URLError as e:
            raise Exception(f"Gemini serveriga ulanib bo'lmadi: {e.reason}")

    raise Exception("Gemini API ishlamadi. Tekshirilgan modellar: " + " | ".join(errors))


def get_user_context(user):
    from apps.tasks.models import Task
    from apps.goals.models import Goal
    from apps.schedule.models import Schedule
    from apps.habits.models import Habit

    today = timezone.now().date()
    current_weekday = [
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
    ][timezone.now().weekday()]

    # Vazifalar
    today_tasks = list(Task.objects.filter(
        user=user, due_date=today, status__in=['pending', 'in_progress']
    ).values('title', 'priority', 'status', 'estimated_minutes'))

    overdue_tasks = list(Task.objects.filter(
        user=user, due_date__lt=today, status__in=['pending', 'in_progress']
    ).values('title', 'priority', 'estimated_minutes'))

    # Maqsadlar
    active_goals = list(Goal.objects.filter(
        user=user, status__in=['pending', 'in_progress']
    ).values('title', 'progress', 'deadline', 'category'))

    # Jadval
    schedule_items = list(
        Schedule.objects.filter(user=user, is_active=True).order_by('start_time')
    )
    today_schedule = [
        {
            'title': s.title,
            'type': s.get_type_display(),
            'start_time': s.start_time.strftime('%H:%M'),
            'end_time': s.end_time.strftime('%H:%M'),
            'location': s.location,
        }
        for s in schedule_items
        if current_weekday in s.get_days_list()
    ]
    weekly_schedule = [
        {
            'title': s.title,
            'type': s.get_type_display(),
            'start_time': s.start_time.strftime('%H:%M'),
            'end_time': s.end_time.strftime('%H:%M'),
            'days': s.get_days_list(),
            'location': s.location,
        }
        for s in schedule_items
    ]

    # === YANGI: Odatlar ===
    habits_qs = Habit.objects.filter(user=user).prefetch_related('completions')
    habits_data = []
    for habit in habits_qs:
        completed_dates = habit.get_completed_dates()
        done_today = today in completed_dates
        habits_data.append({
            'name': habit.name,
            'icon': habit.icon,
            'duration_minutes': habit.duration_minutes,
            'streak': habit.streak,
            'done_today': done_today,
            'total_completions': len(completed_dates),
        })

    # Umumiy kunlik odat vaqti (daqiqalarda)
    total_habit_minutes_daily = sum(h['duration_minutes'] for h in habits_data)
    done_today_count = sum(1 for h in habits_data if h['done_today'])

    # Statistika
    total_tasks = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, status='completed').count()
    completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    return {
        'user_name': user.get_full_name() or user.username,
        'today': today.strftime('%d.%m.%Y'),
        'today_tasks': today_tasks,
        'overdue_tasks': overdue_tasks,
        'active_goals': active_goals,
        'today_schedule': today_schedule,
        'weekly_schedule': weekly_schedule,
        'habits': habits_data,
        'total_habit_minutes_daily': total_habit_minutes_daily,
        'done_today_count': done_today_count,
        'stats': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': completion_rate,
        },
    }


def get_system_prompt(ctx):
    # Jadval band vaqtlarini hisoblash
    schedule_busy_minutes = 0
    for s in ctx['today_schedule']:
        try:
            from datetime import datetime
            start = datetime.strptime(s['start_time'], '%H:%M')
            end = datetime.strptime(s['end_time'], '%H:%M')
            schedule_busy_minutes += int((end - start).total_seconds() / 60)
        except Exception:
            pass

    # Vazifalar uchun taxminiy vaqt
    task_minutes = sum(
        t.get('estimated_minutes') or 0 for t in ctx['today_tasks']
    )

    return (
        "Siz AI Planner ilovasining aqlli yordamchisisiz. "
        "O'zbek tilida javob bering. "
        "Qisqa, aniq va amaliy maslahatlar bering. Emojilardan foydalaning.\n\n"
        "=== FOYDALANUVCHI MA'LUMOTLARI ===\n"
        "Ism: " + ctx['user_name'] + "\n"
        "Bugun: " + ctx['today'] + "\n\n"

        "=== VAZIFALAR ===\n"
        "Bugungi vazifalar (" + str(len(ctx['today_tasks'])) + " ta, taxminiy "
            + str(task_minutes) + " daqiqa): "
            + _json.dumps(ctx['today_tasks'], ensure_ascii=False) + "\n"
        "Kechikkan vazifalar (" + str(len(ctx['overdue_tasks'])) + " ta): "
            + _json.dumps(ctx['overdue_tasks'], ensure_ascii=False) + "\n\n"

        "=== MAQSADLAR ===\n"
        "Faol maqsadlar (" + str(len(ctx['active_goals'])) + " ta): "
            + _json.dumps(ctx['active_goals'], ensure_ascii=False) + "\n\n"

        "=== MY SCHEDULE (JADVAL) ===\n"
        "Bugungi jadval (" + str(len(ctx['today_schedule']))
            + " ta dars/ish, taxminan " + str(schedule_busy_minutes) + " daqiqa band): "
            + _json.dumps(ctx['today_schedule'], ensure_ascii=False) + "\n"
        "Haftalik jadval: "
            + _json.dumps(ctx['weekly_schedule'], ensure_ascii=False) + "\n\n"

        "=== ODATLAR ===\n"
        "Jami odatlar (" + str(len(ctx['habits'])) + " ta, kunlik "
            + str(ctx['total_habit_minutes_daily']) + " daqiqa): "
            + _json.dumps(ctx['habits'], ensure_ascii=False) + "\n"
        "Bugun bajarilgan odatlar: " + str(ctx['done_today_count'])
            + "/" + str(len(ctx['habits'])) + "\n\n"

        "=== STATISTIKA ===\n"
        "Samaradorlik: " + str(ctx['stats']['completion_rate']) + "%\n\n"

        "=== KO'RSATMA ===\n"
        "Yuqoridagi BARCHA ma'lumotlarni hisobga olib maslahat ber:\n"
        "- Jadval band vaqtlarini inobatga ol\n"
        "- Odatlar uchun vaqt ajratishni tavsiya qil\n"
        "- Vazifalar uchun taxminiy vaqtni hisobga ol\n"
        "- Maqsad deadline larini kuzat\n"
        "- Kunlik umumiy yuk (jadval + vazifalar + odatlar) dan kelib chiqib maslahat ber"
    )


def get_ai_advice(user, user_message, advice_type='general'):
    try:
        ctx = get_user_context(user)
        system_prompt = get_system_prompt(ctx)
        ai_response = call_gemini(user_message, system_prompt)

        from .models import AIConversation
        AIConversation.objects.create(
            user=user,
            advice_type=advice_type,
            user_message=user_message,
            ai_response=ai_response,
            tokens_used=0
        )
        return {'success': True, 'response': ai_response}

    except Exception as e:
        return {'success': False, 'error': str(e), 'response': None}


def get_daily_plan(user):
    return get_ai_advice(user,
        "Bugungi kun uchun optimal reja tuzib ber. "
        "Jadvalimdagi band vaqtlarni, odatlarim uchun ketadigan vaqtni va vazifalarimni hisobga olib, "
        "qaysi vazifalardan boshlashim va vaqtni qanday taqsimlashim kerak?",
        advice_type='task_plan')


def get_productivity_tips(user):
    return get_ai_advice(user,
        "Mening statistikam, odatlarim va jadvalim asosida samaradorligimni oshirish uchun "
        "3 ta konkret maslahat ber.",
        advice_type='productivity')