from django.db import models
from django.conf import settings


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', '🟢 Past'),
        ('medium', '🟡 O\'rta'),
        ('high', '🔴 Yuqori'),
        ('urgent', '🚨 Shoshilinch'),
    ]
    STATUS_CHOICES = [
        ('pending', '⏳ Kutmoqda'),
        ('in_progress', '🔄 Jarayonda'),
        ('completed', '✅ Bajarildi'),
        ('cancelled', '❌ Bekor qilindi'),
    ]
    CATEGORY_CHOICES = [
        ('work', '💼 Ish'),
        ('personal', '👤 Shaxsiy'),
        ('study', '📚 O\'qish'),
        ('health', '💪 Sog\'liq'),
        ('finance', '💰 Moliya'),
        ('other', '📌 Boshqa'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='personal')
    
    due_date = models.DateField(null=True, blank=True, verbose_name="Muddat sanasi")
    due_time = models.TimeField(null=True, blank=True, verbose_name="Muddat vaqti")
    
    estimated_minutes = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Taxminiy vaqt (daqiqa)"
    )
    
    goal = models.ForeignKey(
        'goals.Goal',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tasks',
        verbose_name="Bog'liq maqsad"
    )
    
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def is_overdue(self):
        from django.utils import timezone
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return self.due_date < timezone.now().date()
        return False

    def mark_completed(self):
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def toggle_completed(self):
        """
        Statusni 'completed' va 'pending' o'rtasida almashtiradi.
        Qaytishi: yangi status.
        """
        from django.utils import timezone
        if self.status == 'completed':
            self.status = 'pending'
            self.completed_at = None
        else:
            self.status = 'completed'
            self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])
        
        # Maqsad progressini yangilash
        if self.goal:
            self.goal.update_progress()
            
        return self.status

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_goal = None
        if not is_new:
            try:
                old_instance = Task.objects.get(pk=self.pk)
                old_goal = old_instance.goal
            except Task.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Maqsad progressini yangilash
        if self.goal:
            self.goal.update_progress()
        if old_goal and old_goal != self.goal:
            old_goal.update_progress()

    def delete(self, *args, **kwargs):
        goal = self.goal
        super().delete(*args, **kwargs)
        if goal:
            goal.update_progress()

    class Meta:
        verbose_name = "Vazifa"
        verbose_name_plural = "Vazifalar"
        ordering = ['-created_at']
