from itertools import chain

from django.views.generic.base import TemplateView
from tournaments.models import Tournament, Team


class TeamView(TemplateView):
    template_name = 'all_team.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_tournament = Tournament.objects.filter(on_main=True).first()
        if current_tournament:
            context['current_tournament'] = current_tournament
            is_position_teams = current_tournament.team.filter(is_active=True).exclude(position_number=None).order_by('position_number')
            zero_position_teams = current_tournament.team.filter(is_active=True, position_number=None)
            context['teams'] = list(chain(is_position_teams, zero_position_teams))
        return context