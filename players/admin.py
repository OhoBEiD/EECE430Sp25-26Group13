from django.contrib import admin
from .models import VolleyPlayer


class VolleyPlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'date_joined', 'salary', 'contact_person')
    search_fields = ('name', 'contact_person')
    list_filter = ('position',)


admin.site.register(VolleyPlayer, VolleyPlayerAdmin)
