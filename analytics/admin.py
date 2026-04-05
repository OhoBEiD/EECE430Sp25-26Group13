from django.contrib import admin
from .models import PlayerStats


@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'date_recorded', 'overall_score', 'serve_accuracy', 'spike_success')
    list_filter = ('player',)
    search_fields = ('player__name',)
