from django.urls import path
from . import dashboard_views

urlpatterns = [
    path('', dashboard_views.dashboard_view, name='dashboard'),
    path('partials/', dashboard_views.dashboard_partials, name='dashboard_partials'),
]
