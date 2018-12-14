from django.contrib import admin
from .models import Tournament, Team


class TeamInline(admin.TabularInline):
    model = Team
    extra = 0


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'on_main', 'in_calendar',)
    list_editable = ('on_main', 'in_calendar',)
    list_filter = ('on_main', 'in_calendar',)
    inlines = [TeamInline]
