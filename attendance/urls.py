from django.urls import path
from . import views

urlpatterns = [
    path('event/<int:event_pk>/attendance/submit/', views.attendance_submit, name='attendance_submit'),
    path('event/<int:event_pk>/rsvp/submit/', views.rsvp_submit, name='rsvp_submit'),
]
