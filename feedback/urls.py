from django.urls import path
from . import views

urlpatterns = [
    path('event/<int:event_pk>/feedback/submit/', views.feedback_submit, name='feedback_submit'),
]
