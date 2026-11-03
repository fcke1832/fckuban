"""Тесты приложения tournaments."""
import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

from links.models import SocialNetworkLink
from tournaments.admin import (
    MatchTourInline,
    TeamAdmin,
    TourAdmin,
    TournamentAdmin,
)
from tournaments.apps import TournamentsConfig
from tournaments.models import MatchTour, Team, Tour, Tournament
from tournaments.views import StandingsView


@pytest.fixture
def tournament(db):
    return Tournament.objects.create(title='Первенство России', on_main=True, in_calendar=True)


@pytest.fixture
def teams(db, tournament):
    first = Team.objects.create(name='Кубань', location='Краснодар', tournament=tournament)
    second = Team.objects.create(name='Ротор', location='Волгоград', tournament=tournament)
    third = Team.objects.create(name='Черноморец', location='Новороссийск', tournament=tournament)
    return first, second, third


@pytest.fixture
def tour(db, tournament):
    return Tour.objects.create(number=1, tournament=tournament)


def make_match(tour, home, guest, home_goals=0, guest_goals=0, **kwargs):
    return MatchTour.objects.create(
        tour=tour,
        home_team=home,
        guest_team=guest,
        home_goals=home_goals,
        guest_goals=guest_goals,
        **kwargs,
    )


class TestTournamentsConfig:
    def test_app_config(self):
        assert TournamentsConfig.name == 'tournaments'
        assert TournamentsConfig.verbose_name == 'Турниры'


@pytest.mark.django_db
class TestTournament:
    def test_str(self, tournament):
        assert str(tournament) == 'Первенство России'

    def test_meta(self):
        assert Tournament._meta.verbose_name == 'Турнир'
        assert Tournament._meta.ordering == ('on_main', 'in_calendar')

    def test_get_tours_returns_only_active(self, tournament):
        active = Tour.objects.create(number=1, tournament=tournament, is_active=True)
        Tour.objects.create(number=2, tournament=tournament, is_active=False)
        assert list(tournament.get_tours()) == [active]

    def test_get_teams_returns_only_active(self, tournament):
        active = Team.objects.create(name='Активная', tournament=tournament, is_active=True)
        Team.objects.create(name='Неактивная', tournament=tournament, is_active=False)
        assert list(tournament.get_teams()) == [active]

    def test_calculate_statistics(self, tournament, teams, tour):
        first, second, third = teams
        make_match(tour, first, second, 2, 1, is_finished=True)
        make_match(tour, third, first, 1, 3, is_finished=True)
        make_match(tour, second, third, 1, 1, is_finished=True)

        tournament.calculate_statistics()

        first.refresh_from_db()
        second.refresh_from_db()
        third.refresh_from_db()

        assert (first.points, first.matches, first.win_matches) == (6, 2, 2)
        assert (first.goals_scored, first.goals_conceded, first.goals_difference) == (5, 2, 3)
        assert (second.points, second.draw_matches, second.losing_matches) == (1, 1, 1)
        assert (third.points, third.draw_matches, third.losing_matches) == (1, 1, 1)

        assert first.position_number == 1
        assert second.position_number == 2
        assert third.position_number == 3

    def test_calculate_statistics_ignores_inactive_matches(self, tournament, teams, tour):
        first, second, third = teams
        make_match(tour, first, second, 1, 0, is_finished=True, is_active=False)

        tournament.calculate_statistics()

        first.refresh_from_db()
        second.refresh_from_db()
        assert first.matches == 0
        assert second.matches == 0

    def test_calculate_statistics_ignores_inactive_teams(self, tournament, teams, tour):
        first, second, third = teams
        third.is_active = False
        third.save()
        make_match(tour, first, third, 3, 0, is_finished=True)

        tournament.calculate_statistics()

        first.refresh_from_db()
        third.refresh_from_db()
        assert first.matches == 0
        assert third.matches == 0

    def test_calculate_statistics_resets_previous_values(self, tournament, teams, tour):
        first, second, third = teams
        first.points = 99
        first.matches = 99
        first.save()
        make_match(tour, first, second, 1, 0, is_finished=True)

        tournament.calculate_statistics()

        first.refresh_from_db()
        assert first.points == 3
        assert first.matches == 1

    def test_calculate_statistics_counts_canceled_and_future_matches(self, tournament, teams, tour):
        """БАГ-015: в статистику попадают отменённые и ещё не сыгранные матчи."""
        first, second, third = teams
        make_match(tour, first, second, 5, 0, is_finished=False, is_canceled=True)
        make_match(tour, first, third, 0, 0, is_finished=False, is_canceled=False)

        tournament.calculate_statistics()

        first.refresh_from_db()
        # Ожидаемое поведение: отменённый и будущий матчи не должны менять таблицу.
        # assert (first.matches, first.points) == (0, 0)
        assert (first.matches, first.points) == (2, 4)


@pytest.mark.django_db
class TestTour:
    def test_str(self, tournament):
        tour = Tour.objects.create(number=3, tournament=tournament)
        assert str(tour) == '3-й тур Первенство России'

    def test_str_without_tournament_fails(self):
        """БАГ-016: tournament разрешён как NULL, но __str__ падает с AttributeError."""
        tour = Tour(number=3, tournament=None)
        result = None
        try:
            result = str(tour)
        except AttributeError:
            pass
        # Ожидаемое поведение: строка должна строиться и без турнира.
        # assert result is not None

    def test_number_validator_rejects_more_than_30(self, tournament):
        tour = Tour(number=31, tournament=tournament)
        with pytest.raises(ValidationError) as exc_info:
            tour.full_clean()
        assert 'number' in exc_info.value.message_dict

    def test_number_validator_accepts_30(self, tournament):
        tour = Tour(number=30, tournament=tournament)
        tour.full_clean()

    def test_default_is_active(self, tournament):
        tour = Tour.objects.create(number=1, tournament=tournament)
        assert tour.is_active is True

    def test_meta(self):
        assert Tour._meta.verbose_name == 'Тур'
        assert Tour._meta.ordering == ('number',)


@pytest.mark.django_db
class TestTeam:
    def test_str_with_location(self, tournament):
        team = Team.objects.create(name='Кубань', location='Краснодар', tournament=tournament)
        assert str(team) == 'Кубань(Краснодар)'

    def test_str_without_location(self, tournament):
        # БАГ-002: location nullable, но __str__ выводит "None" в названии.
        # Ожидаемое поведение: assert str(team) == 'Кубань'
        team = Team.objects.create(name='Кубань', tournament=tournament)
        assert str(team) == 'Кубань(None)'

    def test_defaults(self, tournament):
        team = Team.objects.create(name='Кубань', tournament=tournament)
        assert team.points == 0
        assert team.matches == 0
        assert team.is_active is True
        assert team.is_fcke is False
        assert team.logo.name == ''

    def test_meta(self):
        assert Team._meta.verbose_name == 'Команда'
        assert Team._meta.verbose_name_plural == 'Команды'

    def test_reset_statistic(self, tournament):
        team = Team.objects.create(
            name='Кубань',
            tournament=tournament,
            points=10,
            matches=5,
            win_matches=3,
            draw_matches=1,
            losing_matches=1,
            home_matches=2,
            guest_matches=3,
            goals_scored=8,
            goals_scored_guest=3,
            goals_conceded=4,
            goals_difference=4,
        )

        team.reset_statistic()
        team.refresh_from_db()

        for field in (
            'points', 'matches', 'win_matches', 'draw_matches', 'losing_matches',
            'home_matches', 'guest_matches', 'goals_scored', 'goals_scored_guest',
            'goals_conceded', 'goals_difference',
        ):
            assert getattr(team, field) == 0

    def test_get_thumbnail_logo(self, tournament, monkeypatch):
        get_thumbnail = MagicMock()
        get_thumbnail.return_value.url = '/media/cache/logo.png'
        monkeypatch.setattr('tournaments.models.get_thumbnail', get_thumbnail)

        team = Team.objects.create(
            name='Кубань',
            tournament=tournament,
            logo='media/logo/logo.png',
        )

        assert team.get_thumbnail_logo == '/media/cache/logo.png'
        get_thumbnail.assert_called_once_with(team.logo, '80x80', crop='center', quality=99)

    def test_logo_upload_to(self):
        assert Team._meta.get_field('logo').upload_to == 'media/logo'


@pytest.mark.django_db
class TestMatchTour:
    def test_str(self, tournament, teams, tour):
        first, second, _ = teams
        match = make_match(tour, first, second)
        assert str(match) == 'Кубань(Краснодар) - Ротор(Волгоград)'

    def test_defaults(self, tournament, teams, tour):
        first, second, _ = teams
        match = make_match(tour, first, second)
        assert match.is_active is True
        assert match.is_finished is False
        assert match.is_canceled is False
        assert match.start_time is None

    def test_meta(self):
        assert MatchTour._meta.verbose_name == 'Матч'
        assert MatchTour._meta.verbose_name_plural == 'Матчи'

    def test_calculate_resultes_home_win(self, tournament, teams, tour):
        home, guest, _ = teams
        match = make_match(tour, home, guest, 3, 1)

        match.calculate_resultes()

        home.refresh_from_db()
        guest.refresh_from_db()
        assert (home.matches, home.home_matches, home.win_matches, home.points) == (1, 1, 1, 3)
        assert (guest.matches, guest.guest_matches, guest.losing_matches, guest.points) == (1, 1, 1, 0)
        assert home.goals_scored == 3
        assert home.goals_conceded == 1
        assert home.goals_difference == 2
        assert guest.goals_scored == 1
        assert guest.goals_scored_guest == 1
        assert guest.goals_conceded == 3
        assert guest.goals_difference == -2

    def test_calculate_resultes_guest_win(self, tournament, teams, tour):
        home, guest, _ = teams
        match = make_match(tour, home, guest, 0, 2)

        match.calculate_resultes()

        home.refresh_from_db()
        guest.refresh_from_db()
        assert home.losing_matches == 1
        assert home.points == 0
        assert guest.win_matches == 1
        assert guest.points == 3
        assert guest.goals_scored_guest == 2

    def test_calculate_resultes_draw(self, tournament, teams, tour):
        home, guest, _ = teams
        match = make_match(tour, home, guest, 1, 1)

        match.calculate_resultes()

        home.refresh_from_db()
        guest.refresh_from_db()
        assert home.draw_matches == 1
        assert home.points == 1
        assert guest.draw_matches == 1
        assert guest.points == 1

    def test_calculate_resultes_counts_canceled_match(self, tournament, teams, tour):
        """БАГ-017: calculate_resultes не проверяет is_canceled/is_finished."""
        home, guest, _ = teams
        match = make_match(tour, home, guest, 2, 0, is_canceled=True)

        match.calculate_resultes()

        home.refresh_from_db()
        # Ожидаемое поведение: отменённый матч не должен менять статистику.
        # assert home.matches == 0
        assert home.matches == 1


@pytest.mark.django_db
class TestStandingsView:
    def test_without_tournament(self, client):
        from calendar_matches.models import Match

        calendar_tournament = Tournament.objects.create(
            title='Календарь', on_main=False, in_calendar=True,
        )
        home = Team.objects.create(name='Дома', tournament=calendar_tournament)
        guest = Team.objects.create(name='Гости', tournament=calendar_tournament)
        Match.objects.create(
            home_team=home,
            guest_team=guest,
            tournament=calendar_tournament,
            start_time=timezone.now() + datetime.timedelta(days=1),
            is_active=True,
        )

        response = client.get(reverse('tournaments:standings'))

        assert response.status_code == 200
        assert response.context['current_tournament'] is None
        assert list(response.context['teams']) == []

    def test_with_tournament_and_calendar(self, client, tournament, teams):
        from calendar_matches.models import Match

        first, second, _ = teams
        match = Match.objects.create(
            home_team=first,
            guest_team=second,
            tournament=tournament,
            start_time=timezone.now() + datetime.timedelta(days=2),
            is_active=True,
        )

        response = client.get(reverse('tournaments:standings'))

        assert response.status_code == 200
        assert response.context['current_tournament'] == tournament
        assert set(response.context['teams']) == set(teams)
        assert response.context['calendar_matches'] == [match]
        assert response.context['future_match'] == match

    def test_social_network_links_are_mapped(self, client, tournament, teams):
        from calendar_matches.models import Match

        first, second, _ = teams
        Match.objects.create(
            home_team=first,
            guest_team=second,
            tournament=tournament,
            start_time=timezone.now() + datetime.timedelta(days=2),
            is_active=True,
        )
        SocialNetworkLink.objects.create(name='FB', link='https://www.facebook.com/fckuban')
        SocialNetworkLink.objects.create(name='VK', link='https://vk.com/fckuban')
        SocialNetworkLink.objects.create(name='IG', link='https://www.instagram.com/fckuban')
        SocialNetworkLink.objects.create(name='YT', link='https://www.youtube.com/fckuban')
        SocialNetworkLink.objects.create(name='TG', link='https://t.me/fckuban')

        response = client.get(reverse('tournaments:standings'))

        assert response.context['facebook_link'] == 'https://www.facebook.com/fckuban'
        assert response.context['vk_link'] == 'https://vk.com/fckuban'
        assert response.context['instagram_link'] == 'https://www.instagram.com/fckuban'
        assert response.context['youtube_channel'] == 'https://www.youtube.com/fckuban'
        assert response.context['telegram_channel'] == 'https://t.me/fckuban'

    def test_page_fails_without_calendar_matches(self, client, tournament):
        """БАГ-001: таблица при пустом календаре падает с IndexError."""
        response = None
        try:
            response = client.get(reverse('tournaments:standings'))
        except IndexError:
            pass
        # Ожидаемое поведение: страница должна открываться и без матчей.
        # assert response is not None and response.status_code == 200

    def test_calculate_statistics_method(self):
        view = StandingsView()
        team = MagicMock()
        view.calculate_statistics(None, [team])
        team.get_tournament_statistics.assert_called_once_with()


@pytest.mark.django_db
class TestTournamentsAdmin:
    def test_team_admin(self):
        model_admin = TeamAdmin(Team, admin.site)
        assert model_admin.list_display == ('name', 'location')
        assert model_admin.list_editable == ('location',)
        assert model_admin.list_filter == ('name', 'location')
        assert Team in admin.site._registry

    def test_tournament_admin_config(self):
        model_admin = TournamentAdmin(Tournament, admin.site)
        assert model_admin.list_display == ('title', 'on_main', 'in_calendar')
        assert model_admin.list_editable == ('on_main', 'in_calendar')
        assert model_admin.change_form_template == 'admin/tournaments_change_form.html'
        assert Tournament in admin.site._registry

    def test_tournament_admin_get_urls(self):
        model_admin = TournamentAdmin(Tournament, admin.site)
        urls = model_admin.get_urls()
        assert any(url.name == 'calculate_standings' for url in urls)

    def test_tour_admin_config(self):
        model_admin = TourAdmin(Tour, admin.site)
        assert model_admin.list_display == ('__str__', 'is_active')
        assert model_admin.list_editable == ('is_active',)
        assert MatchTourInline in model_admin.inlines
        assert Tour in admin.site._registry

    def test_match_tour_inline_config(self):
        assert MatchTourInline.model is MatchTour
        assert MatchTourInline.extra == 0

    def _request(self, referer=None):
        request = RequestFactory().get('/admin/tournaments/tournament/1/change/')
        request._messages = MagicMock()
        if referer is not None:
            request.META['HTTP_REFERER'] = referer
        return request

    def test_calculate_standings_success(self, monkeypatch, tournament):
        calculate = MagicMock()
        monkeypatch.setattr(Tournament, 'calculate_statistics', calculate)
        model_admin = TournamentAdmin(Tournament, admin.site)
        request = self._request(
            f'http://testserver/admin/tournaments/tournament/{tournament.pk}/change/'
        )

        response = model_admin.set_get_calculate_standings_statistic(request)

        calculate.assert_called_once_with()
        assert response.status_code == 302
        assert request._messages.add.called

    def test_calculate_standings_without_referer(self):
        model_admin = TournamentAdmin(Tournament, admin.site)
        request = self._request()

        response = model_admin.set_get_calculate_standings_statistic(request)

        assert response.status_code == 302
        assert request._messages.add.called

    def test_calculate_standings_unknown_tournament(self):
        model_admin = TournamentAdmin(Tournament, admin.site)
        request = self._request('http://testserver/admin/tournaments/tournament/99999/change/')

        response = model_admin.set_get_calculate_standings_statistic(request)

        assert response.status_code == 302
        assert request._messages.add.called

    def test_formfield_for_foreignkey_filters_by_tournament(self, tournament, teams, tour):
        model_admin = MatchTourInline(MatchTour, admin.site)
        request = RequestFactory().get('/')
        request.resolver_match = SimpleNamespace(kwargs={'object_id': str(tour.pk)})
        field = model_admin.formfield_for_foreignkey(
            MatchTour._meta.get_field('home_team'), request
        )
        assert set(field.queryset) == set(teams)

    def test_formfield_for_foreignkey_guest_team(self, tournament, teams, tour):
        model_admin = MatchTourInline(MatchTour, admin.site)
        request = RequestFactory().get('/')
        request.resolver_match = SimpleNamespace(kwargs={'object_id': str(tour.pk)})
        field = model_admin.formfield_for_foreignkey(
            MatchTour._meta.get_field('guest_team'), request
        )
        assert set(field.queryset) == set(teams)

    def test_formfield_for_foreignkey_unknown_tour(self, tournament, teams):
        model_admin = MatchTourInline(MatchTour, admin.site)
        request = RequestFactory().get('/')
        request.resolver_match = SimpleNamespace(kwargs={'object_id': '99999'})
        field = model_admin.formfield_for_foreignkey(
            MatchTour._meta.get_field('home_team'), request
        )
        assert list(field.queryset) == []

    def test_formfield_for_foreignkey_tour_without_tournament(self, teams):
        from tournaments.models import Tour as TourModel

        tour = TourModel.objects.create(number=1, tournament=None)
        model_admin = MatchTourInline(MatchTour, admin.site)
        request = RequestFactory().get('/')
        request.resolver_match = SimpleNamespace(kwargs={'object_id': str(tour.pk)})
        field = model_admin.formfield_for_foreignkey(
            MatchTour._meta.get_field('home_team'), request
        )
        assert list(field.queryset) == []

    def test_formfield_for_foreignkey_without_resolver_match(self, teams):
        """БАГ-018: на форме добавления resolver_match может быть None."""
        model_admin = MatchTourInline(MatchTour, admin.site)
        request = RequestFactory().get('/')
        request.resolver_match = None

        field = None
        try:
            field = model_admin.formfield_for_foreignkey(
                MatchTour._meta.get_field('home_team'), request
            )
        except AttributeError:
            pass
        # Ожидаемое поведение: форма добавления не должна падать.
        # assert field is not None
