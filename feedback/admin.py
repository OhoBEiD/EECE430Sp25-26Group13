from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('player', 'event', 'coach', 'created_at')
    list_filter = ('event__team', 'coach')
    search_fields = ('player__name', 'body')
