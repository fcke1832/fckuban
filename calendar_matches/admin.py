from django.contrib import admin
from tournaments.models import Team
from .models import Match

# class TeamInline(admin.TabularInline):
#     model = Team
#     extra = 2


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'guest_team', 'start_time', 'is_finished', 'is_canceled',)
    list_filter = ('home_team', 'guest_team', 'start_time', 'is_finished', 'is_canceled', 'tour',)
