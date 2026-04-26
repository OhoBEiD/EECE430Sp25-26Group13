from django.urls import path
from . import views

urlpatterns = [
    path('event/<int:event_pk>/lineups/submit/', views.lineup_submit, name='lineup_submit'),
]
