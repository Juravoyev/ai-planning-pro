from django.db import models
from django.conf import settings


class AIConversation(models.Model):
    """AI bilan suhbat tarixi"""
    ADVICE_TYPE_CHOICES = [
        ('general', '💬 Umumiy maslahat'),
        ('task_plan', '📋 Vazifa rejasi'),
        ('time_management', '⏰ Vaqt boshqaruvi'),
        ('goal_advice', '🎯 Maqsad bo\'yicha maslahat'),
        ('productivity', '🚀 Samaradorlik'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_conversations'
    )
    advice_type = models.CharField(max_length=20, choices=ADVICE_TYPE_CHOICES, default='general')
    user_message = models.TextField()
    ai_response = models.TextField()
    tokens_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.advice_type} ({self.created_at.strftime('%d.%m.%Y')})"

    class Meta:
        verbose_name = "AI Suhbat"
        verbose_name_plural = "AI Suhbatlar"
        ordering = ['-created_at']
