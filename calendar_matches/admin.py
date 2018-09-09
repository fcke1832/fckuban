from django.contrib import admin
from .models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'guest_team', 'start_time', 'is_finished', 'is_canceled', 'time_invisible',)
    list_filter = ('home_team', 'guest_team', 'start_time', 'is_finished', 'is_canceled', 'tour',)
    list_editable = ('start_time', 'time_invisible',)
    list_display_links = ('home_team', 'guest_team',)
