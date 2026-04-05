from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('analytics/', include('analytics.urls')),
    path('teams/', include('teams.urls')),
    path('injuries/', include('injuries.urls')),
    path('', include('players.urls')),
]
