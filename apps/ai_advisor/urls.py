from django.urls import path
from . import views

urlpatterns = [
    path('', views.ai_chat_view, name='ai_chat'),
    path('ask/', views.ai_ask, name='ai_ask'),
    path('daily-plan/', views.ai_daily_plan, name='ai_daily_plan'),
    path('productivity/', views.ai_productivity, name='ai_productivity'),
    path('history/', views.conversation_history, name='ai_history'),
]
