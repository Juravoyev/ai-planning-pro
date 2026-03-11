from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'status', 'category', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'user__email', 'user__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
