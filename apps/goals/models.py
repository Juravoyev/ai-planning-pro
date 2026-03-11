from django.db import models
from django.conf import settings


class Goal(models.Model):
    STATUS_CHOICES = [
        ('pending', '⏳ Boshlanmagan'),
        ('in_progress', '🔄 Jarayonda'),
        ('completed', '✅ Bajarildi'),
        ('paused', '⏸️ To\'xtatildi'),
        ('cancelled', '❌ Bekor qilindi'),
    ]
    CATEGORY_CHOICES = [
        ('career', '💼 Karyera'),
        ('education', '📚 Ta\'lim'),
        ('health', '💪 Sog\'liq'),
        ('finance', '💰 Moliya'),
        ('personal', '🌟 Shaxsiy rivojlanish'),
        ('relationship', '❤️ Munosabatlar'),
        ('hobby', '🎨 Hobby'),
        ('other', '📌 Boshqa'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    title = models.CharField(max_length=200, verbose_name="Maqsad nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='personal')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    progress = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Progress (%)"
    )
    
    deadline = models.DateField(null=True, blank=True, verbose_name="Muddat")
    
    # Motivatsiya
    why = models.TextField(blank=True, verbose_name="Nima uchun (motivatsiya)")
    reward = models.CharField(max_length=200, blank=True, verbose_name="Mukofot")
    
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def update_progress(self):
        """Vazifalar asosida progressni yangilash"""
        total_tasks = self.tasks.count()
        if total_tasks > 0:
            completed_tasks = self.tasks.filter(status='completed').count()
            self.progress = int((completed_tasks / total_tasks) * 100)
            if self.progress == 100:
                self.status = 'completed'
                from django.utils import timezone
                self.completed_at = timezone.now()
            elif self.progress > 0:
                self.status = 'in_progress'
            self.save()

    def is_overdue(self):
        from django.utils import timezone
        if self.deadline and self.status not in ['completed', 'cancelled']:
            return self.deadline < timezone.now().date()
        return False

    class Meta:
        verbose_name = "Maqsad"
        verbose_name_plural = "Maqsadlar"
        ordering = ['-created_at']
