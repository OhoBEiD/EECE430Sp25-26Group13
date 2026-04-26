from django.contrib import admin
from .models import Team, Event


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'age_group', 'coach', 'created_at')
    list_filter = ('age_group',)
    search_fields = ('name', 'coach__username', 'coach__last_name')
    autocomplete_fields = ('coach',)


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'team', 'event_type', 'date', 'start_time', 'end_time', 'location')
    list_filter = ('event_type', 'date', 'team')
    search_fields = ('title', 'location')


admin.site.register(Team, TeamAdmin)
admin.site.register(Event, EventAdmin)
