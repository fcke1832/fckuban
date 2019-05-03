from itertools import chain

from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from tournaments.models import Tournament, Team
from fckuban.views import get_hashtag
from .models import Player, Coach


class TeamView(TemplateView):
    template_name = 'all_team.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        players = Player.objects.all()
        context['goalkeepers'] = players.filter(position=Player.GOALKEEPER)
        context['defenders'] = players.filter(position=Player.DEFENDER)
        context['midfielders'] = players.filter(position=Player.MIDFIELDER)
        context['forwards'] = players.filter(position=Player.FORWARD)
        context['coaches'] = Coach.objects.all()
        current_tournament = Tournament.objects.filter(on_main=True).first()
        if current_tournament:
            context['current_tournament'] = current_tournament
            is_position_teams = current_tournament.team.filter(is_active=True).exclude(position_number=None).order_by('position_number')
            zero_position_teams = current_tournament.team.filter(is_active=True, position_number=None)
            context['teams'] = list(chain(is_position_teams, zero_position_teams))
        context['hashtag'] = get_hashtag()
        return context


class PLayerView(DetailView):
    template_name = 'player.html'
    model = Player
    context_object_name = 'player'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['other_players'] = Player.objects.all().exclude(id=kwargs['object'].id)
        return context


class CoachView(DetailView):
    template_name = 'coach.html'
    model = Coach
    context_object_name = 'coach'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
