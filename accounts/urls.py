from django.urls import path

from . import views

urlpatterns = [
    path('me/', views.me_view, name='me'),
    path('coach/', views.coach_landing, name='coach_landing'),
    path('admin-ui/users/', views.admin_user_list, name='admin_user_list'),
    path('admin-ui/users/<int:pk>/edit/', views.admin_user_edit_role, name='admin_user_edit_role'),
]
