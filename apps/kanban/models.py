from django.db import models

# Kanban uchun alohida model kerak emas
# Mavjud Task modelidan foydalanamiz (apps.tasks.models.Task)
# Task.status maydoni Kanban ustunlari sifatida ishlatiladi:
# pending     -> "Yangi"
# in_progress -> "Jarayonda"
# completed   -> "Bajarildi"
