from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_index, name='chat_index'),
    path('<int:thread_id>/', views.chat_room, name='chat_room'),
]
