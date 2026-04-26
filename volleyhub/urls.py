from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('accounts.urls')),
    path('analytics/', include('analytics.urls')),
    path('teams/', include('teams.urls')),
    path('injuries/', include('injuries.urls')),
    path('players/', include('players.urls')),
    path('', include('attendance.urls')),
    path('', include('feedback.urls')),
    path('', include('lineups.urls')),
    path('chat/', include('chat.urls')),
    path('', views.dashboard, name='dashboard'),
]
