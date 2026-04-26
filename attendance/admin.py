from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('player', 'event', 'status', 'marked_at', 'marked_by')
    list_filter = ('status', 'event__team')
    search_fields = ('player__name', 'event__title')
