from django.contrib import admin
from .models import AIConversation


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'advice_type', 'tokens_used', 'created_at')
    list_filter = ('advice_type', 'created_at')
    search_fields = ('user__email', 'user_message')
    ordering = ('-created_at',)
    readonly_fields = ('user_message', 'ai_response', 'tokens_used', 'created_at')
