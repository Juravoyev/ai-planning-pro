import urllib.request
import urllib.error
import json as _json
from django.conf import settings
from django.utils import timezone


def call_gemini(user_message, system_prompt):
    """Google Gemini API"""
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key or api_key == 'your_gemini_api_key_here':
        raise Exception("Gemini API kaliti topilmadi yoki u hali o'zgartirilmagan. .env faylida GEMINI_API_KEY ni haqiqiy kalit bilan almashtiring.")

    payload = _json.dumps({
        "contents": [{
            "parts": [{
                "text": f"System Instruction: {system_prompt}\n\nUser Message: {user_message}"
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000,
        }
    }).encode("utf-8")

    configured_model = getattr(settings, 'GEMINI_MODEL', '').strip()
    model_candidates = [model for model in [
        configured_model,
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
    ] if model]

    errors = []
    for model_name in model_candidates:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        })

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = _json.loads(resp.read())

            if 'candidates' in data and data['candidates']:
                parts = data['candidates'][0].get('content', {}).get('parts', [])
                response_text = "\n".join(
                    part.get('text', '').strip() for part in parts if part.get('text')
                ).strip()
                if response_text:
                    return response_text
            raise Exception("Gemini dan bo'sh javob qaytdi.")

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

    today = timezone.now().date()
    current_weekday = [
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
    ][timezone.now().weekday()]

    today_tasks = list(Task.objects.filter(
        user=user, due_date=today, status__in=['pending', 'in_progress']
    ).values('title', 'priority', 'status'))

    overdue_tasks = list(Task.objects.filter(
        user=user, due_date__lt=today, status__in=['pending', 'in_progress']
    ).values('title', 'priority'))

    active_goals = list(Goal.objects.filter(
        user=user, status__in=['pending', 'in_progress']
    ).values('title', 'progress'))

    schedule_items = list(
        Schedule.objects.filter(user=user, is_active=True).order_by('start_time')
    )
    today_schedule = [
        {
            'title': schedule.title,
            'type': schedule.get_type_display(),
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'location': schedule.location,
        }
        for schedule in schedule_items
        if current_weekday in schedule.get_days_list()
    ]
    weekly_schedule = [
        {
            'title': schedule.title,
            'type': schedule.get_type_display(),
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'days': schedule.get_days_list(),
            'location': schedule.location,
        }
        for schedule in schedule_items
    ]

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
        'stats': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': completion_rate,
        },
    }


def get_system_prompt(ctx):
    return (
        "Siz AI Planner ilovasining aqlli yordamchisisiz. "
        "O'zbek tilida javob bering. "
        "Qisqa, aniq va amaliy maslahatlar bering. Emojilardan foydalaning.\n\n"
        "Foydalanuvchi: " + ctx['user_name'] + "\n"
        "Bugun: " + ctx['today'] + "\n"
        "Bugungi vazifalar (" + str(len(ctx['today_tasks'])) + " ta): "
            + _json.dumps(ctx['today_tasks'], ensure_ascii=False) + "\n"
        "Kechikkan vazifalar (" + str(len(ctx['overdue_tasks'])) + " ta): "
            + _json.dumps(ctx['overdue_tasks'], ensure_ascii=False) + "\n"
        "Faol maqsadlar (" + str(len(ctx['active_goals'])) + " ta): "
            + _json.dumps(ctx['active_goals'], ensure_ascii=False) + "\n"
        "Bugungi jadval (" + str(len(ctx['today_schedule'])) + " ta): "
            + _json.dumps(ctx['today_schedule'], ensure_ascii=False) + "\n"
        "Haftalik jadval: "
            + _json.dumps(ctx['weekly_schedule'], ensure_ascii=False) + "\n"
        "Jadvaldagi band vaqtlarni inobatga olib tavsiya bering.\n"
        "Samaradorlik: " + str(ctx['stats']['completion_rate']) + "%"
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
        "Jadvalimdagi band vaqtlarni hisobga olib, qaysi vazifalardan boshlashim va vaqtni qanday taqsimlashim kerak?",
        advice_type='task_plan')


def get_productivity_tips(user):
    return get_ai_advice(user,
        "Mening statistikam asosida samaradorligimni oshirish uchun 3 ta konkret maslahat ber.",
        advice_type='productivity')
