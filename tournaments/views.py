from django.views.generic.base import TemplateView
from .models import Tournament


class StandingsView(TemplateView):
    template_name = 'full_standings.html'

    # TODO
    def calculate_statistics(self, tournament, teams):
        for team in teams:
            team.get_tournament_statistics()

    def get_context_data(self, **kwargs):
        context = super(StandingsView, self).get_context_data(**kwargs)
        try:
            current_tournament = Tournament.objects.filter(on_main=True)[0]
            teams = current_tournament.team.filter(is_active=True)
        except IndexError:
            current_tournament = None
            teams = []
        # sorted_teams = self.calculate_statistics(current_tournament, teams)
        context['current_tournament'] = current_tournament
        context['teams'] = teams
        return context
