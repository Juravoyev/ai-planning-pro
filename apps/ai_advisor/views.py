from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .services import get_ai_advice, get_daily_plan, get_productivity_tips
from .models import AIConversation


@login_required
def ai_chat_view(request):
    """AI chat sahifasi"""
    # So'nggi 10 ta suhbat
    recent_conversations = AIConversation.objects.filter(
        user=request.user
    )[:10]

    advice_types = AIConversation.ADVICE_TYPE_CHOICES

    context = {
        'recent_conversations': recent_conversations,
        'advice_types': advice_types,
    }
    return render(request, 'ai_advisor/chat.html', context)


@login_required
@require_POST
def ai_ask(request):
    """AJAX: AI ga savol berish"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        advice_type = data.get('advice_type', 'general')

        if not user_message:
            return JsonResponse({'success': False, 'error': 'Xabar bosh bolishi mumkin emas'})

        result = get_ai_advice(request.user, user_message, advice_type)

        if result['success']:
            return JsonResponse({
                'success': True,
                'response': result['response'],
                'tokens': result.get('tokens', 0)
            })
        else:
            error_msg = result.get('error', 'Nomalum xato')
            return JsonResponse({
                'success': False,
                'error': f"AI xato: {error_msg}"
            })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': "Noto'g'ri so'rov formati"})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def ai_daily_plan(request):
    """Kunlik reja olish"""
    result = get_daily_plan(request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(result)
    return render(request, 'ai_advisor/daily_plan.html', {'result': result})


@login_required
def ai_productivity(request):
    """Samaradorlik maslahati"""
    result = get_productivity_tips(request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(result)
    return render(request, 'ai_advisor/productivity.html', {'result': result})


@login_required
def conversation_history(request):
    """Suhbat tarixi"""
    conversations = AIConversation.objects.filter(user=request.user)
    return render(request, 'ai_advisor/history.html', {'conversations': conversations})