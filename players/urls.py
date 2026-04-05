from django.urls import path
from . import views

urlpatterns = [
    path('', views.player_list, name='player_list'),
    path('player/<int:pk>/', views.player_detail, name='player_detail'),
    path('player/add/', views.player_add, name='player_add'),
    path('player/<int:pk>/edit/', views.player_edit, name='player_edit'),
    path('player/<int:pk>/delete/', views.player_delete, name='player_delete'),
]
