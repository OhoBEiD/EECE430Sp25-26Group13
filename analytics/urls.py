from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_select, name='analytics_select'),
    path('<int:player_pk>/', views.analytics_dashboard, name='analytics_dashboard'),
    path('<int:player_pk>/record/', views.record_stats, name='record_stats'),
    path('stats/<int:pk>/delete/', views.stats_delete, name='stats_delete'),
]
