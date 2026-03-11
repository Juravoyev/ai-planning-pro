from django.contrib import admin
from .models import Goal


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'progress', 'deadline', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'user__email')
    ordering = ('-created_at',)
