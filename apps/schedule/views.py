from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.template.loader import render_to_string
import json
from .models import Schedule


DAYS_UZ = {
    'monday': 'Dushanba', 'tuesday': 'Seshanba', 'wednesday': 'Chorshanba',
    'thursday': 'Payshanba', 'friday': 'Juma', 'saturday': 'Shanba', 'sunday': 'Yakshanba'
}
DAYS_ORDER = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
TODAY_MAP = {0:'monday',1:'tuesday',2:'wednesday',3:'thursday',4:'friday',5:'saturday',6:'sunday'}
COLORS = {
    'blue':'#5b7fff','purple':'#9b5de5','pink':'#f72585',
    'green':'#06d6a0','yellow':'#ffbe0b','orange':'#ff6b35'
}

def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _build_schedule_context(user):
    now = timezone.now()
    today_key = TODAY_MAP[now.weekday()]
    current_time = now.time()

    schedules = Schedule.objects.filter(user=user)

    # Har bir jadval uchun computed fieldlar
    for s in schedules:
        s.days_list = s.get_days_list()
        s.color_value = COLORS.get(s.color, '#5b7fff')
        s.dur = s.duration_minutes()

    # Haftalik grid uchun: har kun, har soat
    hours = list(range(7, 21))  # 07:00 - 20:00

    # Grid: {day: {hour: [schedules]}}
    grid = {day: {h: [] for h in hours} for day in DAYS_ORDER}

    for s in schedules:
        if not s.is_active:
            continue
        for day in s.days_list:
            if day not in grid:
                continue
            s_hour = s.start_time.hour
            e_hour = s.end_time.hour
            for h in hours:
                if h >= s_hour and h < e_hour:
                    grid[day][h].append(s)

    # Bugungi jadvallar
    today_schedules = [s for s in schedules if today_key in s.days_list and s.is_active]
    today_schedules.sort(key=lambda x: x.start_time)

    # Hozir o'tayotgan dars
    current_class = next(
        (s for s in today_schedules if s.start_time <= current_time <= s.end_time), None
    )
    # Keyingi dars
    next_class = next(
        (s for s in today_schedules if s.start_time > current_time), None
    )

    return {
        'schedules': schedules,
        'days_order': DAYS_ORDER,
        'days_uz': DAYS_UZ,
        'hours': hours,
        'grid': grid,
        'today_key': today_key,
        'today_schedules': today_schedules,
        'current_class': current_class,
        'next_class': next_class,
        'colors': COLORS,
        'color_choices': list(COLORS.items()),
        'type_choices': Schedule.TYPE_CHOICES,
        'active_count': schedules.filter(is_active=True).count(),
    }


@login_required
def schedule_view(request):
    context = _build_schedule_context(request.user)
    return render(request, 'schedule/schedule.html', context)

@login_required
def schedule_partials(request):
    """
    Sahifani refresh qilmasdan yangilash uchun (AJAX).
    """
    if not _is_ajax(request):
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    context = _build_schedule_context(request.user)
    return JsonResponse({
        'success': True,
        'info_html': render_to_string('schedule/_info_cards.html', context, request=request),
        'list_html': render_to_string('schedule/_schedule_list.html', context, request=request),
        'grid_html': render_to_string('schedule/_week_grid.html', context, request=request),
    })


@login_required
@require_POST
def schedule_create(request):
    data = request.POST
    days_list = request.POST.getlist('days')
    if not days_list:
        if _is_ajax(request):
            return JsonResponse({'success': False, 'error': "Kamida bitta kun tanlang!"}, status=400)
        messages.error(request, "Kamida bitta kun tanlang!")
        return redirect('schedule')

    Schedule.objects.create(
        user=request.user,
        title=data.get('title'),
        type=data.get('type', 'class'),
        icon=data.get('icon', '🎓'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        location=data.get('location', ''),
        description=data.get('description', ''),
        color=data.get('color', 'blue'),
        days=','.join(days_list),
    )
    if _is_ajax(request):
        return JsonResponse({'success': True, 'message': "✅ Jadval qo'shildi!"})
    messages.success(request, "✅ Jadval qo'shildi!")
    return redirect('schedule')


@login_required
@require_POST
def schedule_edit(request, pk):
    s = get_object_or_404(Schedule, pk=pk, user=request.user)
    days_list = request.POST.getlist('days')
    if not days_list:
        if _is_ajax(request):
            return JsonResponse({'success': False, 'error': "Kamida bitta kun tanlang!"}, status=400)
        messages.error(request, "Kamida bitta kun tanlang!")
        return redirect('schedule')

    s.title = request.POST.get('title', s.title)
    s.type = request.POST.get('type', s.type)
    s.icon = request.POST.get('icon', s.icon)
    s.start_time = request.POST.get('start_time', s.start_time)
    s.end_time = request.POST.get('end_time', s.end_time)
    s.location = request.POST.get('location', '')
    s.description = request.POST.get('description', '')
    s.color = request.POST.get('color', s.color)
    s.days = ','.join(days_list)
    s.save()
    if _is_ajax(request):
        return JsonResponse({'success': True, 'message': "✅ Jadval yangilandi!"})
    messages.success(request, "✅ Jadval yangilandi!")
    return redirect('schedule')


@login_required
@require_POST
def schedule_toggle(request, pk):
    s = get_object_or_404(Schedule, pk=pk, user=request.user)
    s.is_active = not s.is_active
    s.save()
    return JsonResponse({'success': True, 'is_active': s.is_active})


@login_required
@require_POST
def schedule_delete(request, pk):
    s = get_object_or_404(Schedule, pk=pk, user=request.user)
    s.delete()
    if _is_ajax(request):
        return JsonResponse({'success': True, 'message': "🗑️ Jadval o'chirildi."})
    messages.success(request, "🗑️ Jadval o'chirildi.")
    return redirect('schedule')
