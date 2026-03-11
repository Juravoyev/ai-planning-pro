from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Kengaytirilgan foydalanuvchi modeli"""
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Foydalanuvchi odatlari (AI uchun)
    work_start_time = models.TimeField(null=True, blank=True, help_text="Ish boshlash vaqti")
    work_end_time = models.TimeField(null=True, blank=True, help_text="Ish tugash vaqti")
    preferred_language = models.CharField(
        max_length=10,
        choices=[('uz', "O'zbek"), ('ru', 'Русский'), ('en', 'English')],
        default='uz'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
