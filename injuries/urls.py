from django.urls import path
from . import views

urlpatterns = [
    path('', views.injury_list, name='injury_list'),
    path('<int:pk>/', views.injury_detail, name='injury_detail'),
    path('create/', views.injury_create, name='injury_create'),
    path('<int:pk>/edit/', views.injury_edit, name='injury_edit'),
    path('<int:pk>/delete/', views.injury_delete, name='injury_delete'),
]
