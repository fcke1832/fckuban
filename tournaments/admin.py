from django.contrib import admin
from .models import Tournament, Team, MatchTour, Tour


class TeamInline(admin.TabularInline):
    model = Team
    extra = 0


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'on_main', 'in_calendar',)
    list_editable = ('on_main', 'in_calendar',)
    list_filter = ('on_main', 'in_calendar',)
    inlines = [TeamInline]


class MatchTourInline(admin.TabularInline):
    model = MatchTour
    extra = 0


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('number', 'is_active',)
    list_filter = ('number', 'is_active',)
    inlines = [MatchTourInline]
