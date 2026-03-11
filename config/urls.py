from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from apps.users.focus_view import focus_view
from apps.users.analytics_view import analytics_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard') if request.user.is_authenticated else redirect('login'), name='home'),
    path('users/', include('apps.users.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('goals/', include('apps.goals.urls')),
    path('ai/', include('apps.ai_advisor.urls')),
    path('dashboard/', include('apps.users.dashboard_urls')),
    path('kanban/', include('apps.kanban.urls')),
    path('schedule/', include('apps.schedule.urls')),
    path('habits/', include('apps.habits.urls')),
    path('focus/', focus_view, name='focus'),
    path('analytics/', analytics_view, name='analytics'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
