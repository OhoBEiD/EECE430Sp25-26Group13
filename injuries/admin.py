from django.contrib import admin
from .models import Injury


class InjuryAdmin(admin.ModelAdmin):
    list_display = ('player', 'injury_type', 'severity', 'body_part', 'status', 'date_reported')
    list_filter = ('severity', 'status', 'body_part')
    search_fields = ('player__name',)


admin.site.register(Injury, InjuryAdmin)
