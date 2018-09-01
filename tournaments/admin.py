from django.contrib import admin
from .models import Tournament, Team


class TeamInline(admin.TabularInline):
    model = Team
    extra = 0


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'on_main',)
    list_editable = ('on_main',)
    list_filter = ('on_main',)
    inlines = [TeamInline]
