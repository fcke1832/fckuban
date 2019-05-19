from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path

from .models import Tournament, Team, MatchTour, Tour


class TeamInline(admin.TabularInline):
    model = Team
    extra = 0


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'on_main', 'in_calendar',)
    list_editable = ('on_main', 'in_calendar',)
    list_filter = ('on_main', 'in_calendar',)
    change_form_template = "admin/tournaments_change_form.html"
    inlines = [TeamInline]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('calculate_standings/', self.set_get_calculate_standings_statistic, name='calculate_standings')
        ]
        return my_urls + urls

    def set_get_calculate_standings_statistic(self, request):
        """
        Функция для пересчета положения команд в таблице
        """
        try:
            tournament_id = request.META.get('HTTP_REFERER').split('/')[-3]
        except:
            self.message_user(request, "Турнир не найден", level=messages.ERROR)
            return HttpResponseRedirect("../")
        try:
            current_tournament = self.model.objects.get(pk=tournament_id)
        except:
            self.message_user(request, "Турнир не найден", level=messages.ERROR)
            return HttpResponseRedirect("../")
        current_tournament.calculate_statistics()
        self.message_user(request, "Таблица пересчитана успешно")
        return HttpResponseRedirect("../")


class MatchTourInline(admin.TabularInline):
    model = MatchTour
    extra = 0

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Фильтрация команд по текущему турниру
        """
        field = super(MatchTourInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'home_team' or db_field.name == 'guest_team':
            try:
                matchtour = MatchTour.objects.get(pk=request.path_info.split('/')[-3])
                tournament = matchtour.tour.tournament
                field.queryset = field.queryset.filter(tournament=tournament)
            except:
                field.queryset = field.queryset.none()

        return field


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active',)
    list_filter = ('number', 'is_active',)
    list_editable = ('is_active',)
    inlines = [MatchTourInline]
