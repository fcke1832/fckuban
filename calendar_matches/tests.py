"""Тесты приложения calendar_matches."""
import datetime

import pytest
from django.contrib import admin
from django.utils import timezone

import calendar_matches.views  # noqa: F401
from calendar_matches.admin import MatchAdmin
from calendar_matches.apps import CalendarMatchesConfig
from calendar_matches.models import Match
from tickets.models import TicketProgram
from tournaments.models import Team, Tournament


@pytest.fixture
def tournament(db):
    return Tournament.objects.create(title='Первенство России')


@pytest.fixture
def teams(db, tournament):
    home = Team.objects.create(name='Кубань', location='Краснодар', tournament=tournament)
    guest = Team.objects.create(name='Ротор', location='Волгоград', tournament=tournament)
    return home, guest


class TestCalendarMatchesConfig:
    def test_app_config(self):
        assert CalendarMatchesConfig.name == 'calendar_matches'


@pytest.mark.django_db
class TestMatchModel:
    def test_str(self, teams, tournament):
        home, guest = teams
        match = Match.objects.create(
            home_team=home,
            guest_team=guest,
            tournament=tournament,
            start_time=timezone.now(),
        )
        assert str(match) == 'Кубань(Краснодар) - Ротор(Волгоград)'

    def test_defaults(self, teams, tournament):
        home, guest = teams
        match = Match.objects.create(home_team=home, guest_team=guest, tournament=tournament)
        assert match.is_active is False
        assert match.is_finished is False
        assert match.is_canceled is False
        assert match.home_goals == 0
        assert match.guest_goals == 0
        assert match.time_invisible is False
        assert match.ticket_program is None
        assert match.link_tickets is None

    def test_start_time_is_nullable(self, teams, tournament):
        home, guest = teams
        match = Match.objects.create(
            home_team=home,
            guest_team=guest,
            tournament=tournament,
            start_time=None,
        )
        assert match.start_time is None

    def test_ticket_program_set_null_on_delete(self, teams, tournament):
        home, guest = teams
        program = TicketProgram.objects.create(name='Сезон')
        match = Match.objects.create(
            home_team=home,
            guest_team=guest,
            tournament=tournament,
            ticket_program=program,
        )
        program.delete()
        match.refresh_from_db()
        assert match.ticket_program is None

    def test_meta_ordering(self, teams, tournament):
        home, guest = teams
        old = Match.objects.create(
            home_team=home,
            guest_team=guest,
            tournament=tournament,
            start_time=timezone.now() - datetime.timedelta(days=1),
        )
        new = Match.objects.create(
            home_team=home,
            guest_team=guest,
            tournament=tournament,
            start_time=timezone.now(),
        )
        assert list(Match.objects.all()) == [new, old]

    def test_related_names(self, teams, tournament):
        home, guest = teams
        match = Match.objects.create(home_team=home, guest_team=guest, tournament=tournament)
        assert list(home.home_match.all()) == [match]
        assert list(guest.guest_match.all()) == [match]
        assert list(tournament.match.all()) == [match]


@pytest.mark.django_db
class TestMatchAdmin:
    def test_registered_and_config(self):
        model_admin = MatchAdmin(Match, admin.site)
        assert model_admin.list_display == (
            'home_team',
            'guest_team',
            'start_time',
            'is_finished',
            'is_canceled',
            'time_invisible',
            'is_active',
        )
        assert model_admin.list_editable == ('start_time', 'time_invisible', 'is_active')
        assert model_admin.list_display_links == ('home_team', 'guest_team')
        assert 'is_finished' in model_admin.list_filter
        assert Match in admin.site._registry
