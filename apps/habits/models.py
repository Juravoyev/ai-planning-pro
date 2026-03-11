from django.db import models
from django.conf import settings


class Habit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=200, verbose_name="Odat nomi")
    icon = models.CharField(max_length=10, default='💪')
    streak = models.IntegerField(default=0, verbose_name="Streak")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_last7_dates(self):
        from datetime import date, timedelta
        today = date.today()
        return [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    def get_completed_dates(self):
        return set(self.completions.values_list('date', flat=True))

    def recalc_streak(self):
        from datetime import date, timedelta
        completed = self.get_completed_dates()
        streak = 0
        d = date.today()
        while d in completed:
            streak += 1
            d -= timedelta(days=1)
        self.streak = streak
        self.save(update_fields=['streak'])

    class Meta:
        ordering = ['created_at']
        verbose_name = "Odat"
        verbose_name_plural = "Odatlar"


class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField()

    class Meta:
        unique_together = ('habit', 'date')
        ordering = ['-date']
