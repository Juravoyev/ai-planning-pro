from django.db import models
from django.conf import settings


class Schedule(models.Model):
    TYPE_CHOICES = [
        ('class', '🎓 Dars / Ta\'lim'),
        ('work', '💼 Ish'),
        ('personal', '👤 Shaxsiy'),
        ('gym', '💪 Sport / Gym'),
        ('other', '📌 Boshqa'),
    ]
    COLOR_CHOICES = [
        ('blue',   '#5b7fff'),
        ('purple', '#9b5de5'),
        ('pink',   '#f72585'),
        ('green',  '#06d6a0'),
        ('yellow', '#ffbe0b'),
        ('orange', '#ff6b35'),
    ]
    # Hafta kunlari — ko'p tanlash uchun
    DAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='class')
    icon = models.CharField(max_length=10, default='🎓')
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='blue')
    is_active = models.BooleanField(default=True)

    # Hafta kunlari — vergul bilan ajratilgan string
    # masalan: "monday,tuesday,wednesday"
    days = models.CharField(max_length=100, default='monday')

    created_at = models.DateTimeField(auto_now_add=True)

    def get_days_list(self):
        return [d.strip() for d in self.days.split(',') if d.strip()]

    def duration_minutes(self):
        from datetime import datetime, date
        s = datetime.combine(date.today(), self.start_time)
        e = datetime.combine(date.today(), self.end_time)
        return max(0, int((e - s).seconds / 60))

    def color_hex(self):
        colors = {
            'blue': '#5b7fff', 'purple': '#9b5de5', 'pink': '#f72585',
            'green': '#06d6a0', 'yellow': '#ffbe0b', 'orange': '#ff6b35',
        }
        return colors.get(self.color, '#5b7fff')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['start_time']
        verbose_name = "Jadval"
        verbose_name_plural = "Jadvallar"
