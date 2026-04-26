from django.contrib import admin
from .models import LineupSlot

@admin.register(LineupSlot)
class LineupSlotAdmin(admin.ModelAdmin):
    list_display = ('event', 'position', 'player')
    list_filter = ('event__team', 'position')
    search_fields = ('player__name', 'event__title')
