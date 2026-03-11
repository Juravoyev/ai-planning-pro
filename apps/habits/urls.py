from django.urls import path
from . import views

urlpatterns = [
    path('', views.habits_view, name='habits'),
    path('partials/', views.habits_partials, name='habits_partials'),
    path('create/', views.habit_create, name='habit_create'),
    path('toggle/<int:pk>/', views.habit_toggle, name='habit_toggle'),
    path('delete/<int:pk>/', views.habit_delete, name='habit_delete'),
]
