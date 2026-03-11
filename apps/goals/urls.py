from django.urls import path
from . import views

urlpatterns = [
    path('', views.goal_list, name='goal_list'),
    path('create/', views.goal_create, name='goal_create'),
    path('<int:pk>/', views.goal_detail, name='goal_detail'),
    path('<int:pk>/edit/', views.goal_edit, name='goal_edit'),
    path('<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    path('<int:pk>/progress/', views.goal_update_progress, name='goal_update_progress'),
    path('<int:pk>/partials/', views.goal_detail_partials, name='goal_detail_partials'),
]
