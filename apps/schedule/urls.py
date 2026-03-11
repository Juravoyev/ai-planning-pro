from django.urls import path
from . import views

urlpatterns = [
    path('', views.schedule_view, name='schedule'),
    path('partials/', views.schedule_partials, name='schedule_partials'),
    path('create/', views.schedule_create, name='schedule_create'),
    path('edit/<int:pk>/', views.schedule_edit, name='schedule_edit'),
    path('toggle/<int:pk>/', views.schedule_toggle, name='schedule_toggle'),
    path('delete/<int:pk>/', views.schedule_delete, name='schedule_delete'),
]
