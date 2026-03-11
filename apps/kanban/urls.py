from django.urls import path
from . import views

urlpatterns = [
    path('', views.kanban_board, name='kanban'),
    path('update-status/', views.update_task_status, name='kanban_update_status'),
]
