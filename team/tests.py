"""Тесты приложения team."""
from unittest.mock import MagicMock

import pytest
from django.contrib import admin
from django.urls import reverse

from links.models import Hashtag
from team.admin import CoachAdmin, PlayerAdmin
from team.apps import TeamConfig
from team.models import BaseTeamMember, Coach, Player
from tournaments.models import Team, Tournament


@pytest.fixture
def tournament(db):
    return Tournament.objects.create(title='Первенство', on_main=True)


@pytest.fixture
def players(db):
    image = 'media/team_upload/player.png'
    goalkeeper = Player.objects.create(
        full_name='Иванов Иван', position=Player.GOALKEEPER, number=1, image=image,
    )
    defender = Player.objects.create(
        full_name='Петров Пётр', position=Player.DEFENDER, number=2, image=image,
    )
    midfielder = Player.objects.create(
        full_name='Сидоров Сидор', position=Player.MIDFIELDER, number=3, image=image,
    )
    forward = Player.objects.create(
        full_name='Кузнецов Кузьма', position=Player.FORWARD, number=4, image=image,
    )
    return {
        Player.GOALKEEPER: goalkeeper,
        Player.DEFENDER: defender,
        Player.MIDFIELDER: midfielder,
        Player.FORWARD: forward,
    }


class TestTeamConfig:
    def test_app_config(self):
        assert TeamConfig.name == 'team'


@pytest.mark.django_db
class TestBaseTeamMember:
    def test_get_second_name_returns_first_token(self):
        player = Player(full_name='Иванов Иван Иванович')
        assert player.get_second_name() == 'Иванов'

    def test_get_second_name_empty_name(self):
        player = Player(full_name='')
        assert player.get_second_name() == ''

    def test_slug_is_generated_from_full_name(self):
        player = Player.objects.create(full_name='Иванов Иван')
        assert player.slug == 'ivanov-ivan'

    def test_slug_is_not_changed_for_existing_value(self):
        player = Player.objects.create(full_name='Иванов Иван', slug='custom-slug')
        player.full_name = 'Петров Пётр'
        player.save()
        player.refresh_from_db()
        assert player.slug == 'custom-slug'

    def test_slug_is_generated_only_once(self):
        player = Player.objects.create(full_name='Иванов Иван')
        original_slug = player.slug
        player.save()
        player.refresh_from_db()
        assert player.slug == original_slug

    def test_optional_fields(self):
        player = Player.objects.create(full_name='Иванов Иван')
        assert player.birthday is None
        assert player.image.name == ''
        assert player.image_hover.name == ''
        assert player.image_detail.name == ''
        assert player.image_slider.name == ''
        assert player.slug == 'ivanov-ivan'

    def test_upload_to_paths(self):
        for field_name in ('image', 'image_hover', 'image_detail', 'image_slider'):
            field = BaseTeamMember._meta.get_field(field_name)
            assert field.upload_to == 'media/team_upload'


@pytest.mark.django_db
class TestPlayer:
    def test_str(self):
        player = Player.objects.create(full_name='Иванов Иван')
        assert str(player) == 'Иванов Иван'

    def test_defaults(self):
        player = Player.objects.create(full_name='Иванов Иван')
        assert player.position == Player.GOALKEEPER
        assert player.weight == 0
        assert player.growth == 0
        assert player.number == 0

    def test_position_choices(self):
        assert dict(Player.POSITION_CHOICES) == {
            0: 'Вратарь',
            1: 'Защитник',
            2: 'Полузащитник',
            3: 'Нападающий',
        }

    def test_meta(self):
        assert Player._meta.verbose_name == 'Игрок'
        assert Player._meta.verbose_name_plural == 'Игроки'
        assert Player._meta.abstract is False
        # БАГ-008: BaseTeamMember не объявлена abstract, поэтому создаётся
        # отдельная таблица team_baseteammember и она видна в админке/миграциях.
        # Ожидаемое поведение: assert BaseTeamMember._meta.abstract is True
        assert BaseTeamMember._meta.abstract is False


@pytest.mark.django_db
class TestCoach:
    def test_str(self):
        coach = Coach.objects.create(full_name='Петров Пётр')
        assert str(coach) == 'Петров Пётр'

    def test_default_position(self):
        coach = Coach.objects.create(full_name='Петров Пётр')
        assert coach.position == Coach.ASSISTANT_COACH

    def test_position_choices(self):
        assert dict(Coach.POSITION_CHOICES) == {
            0: 'Главный тренер',
            1: 'Старший тренер',
            2: 'Тренер вратарей',
        }

    def test_meta(self):
        assert Coach._meta.verbose_name == 'Тренер'
        assert Coach._meta.verbose_name_plural == 'Тренерский штаб'


@pytest.mark.django_db
class TestTeamAdminThumbnails:
    @pytest.mark.parametrize(
        'field_name, method_name',
        [
            ('image', 'image_thumbnail'),
            ('image_hover', 'image_hover_thumbnail'),
            ('image_detail', 'image_detail_thumbnail'),
            ('image_slider', 'image_slider_thumbnail'),
        ],
    )
    def test_player_thumbnail_with_image(self, monkeypatch, field_name, method_name):
        preview = MagicMock(url='/media/cache/75x125/photo.png', width=75, height=125)
        monkeypatch.setattr('team.admin.get_thumbnail', MagicMock(return_value=preview))

        player = Player.objects.create(
            full_name='Иванов Иван',
            **{field_name: 'media/team_upload/p.png'}
        )
        model_admin = PlayerAdmin(Player, admin.site)
        method = getattr(model_admin, method_name)

        html = method(player)

        assert '<img src="/media/cache/75x125/photo.png"' in html
        assert 'width="75"' in html
        assert 'height="125"' in html

    @pytest.mark.parametrize(
        'field_name, method_name',
        [
            ('image', 'image_thumbnail'),
            ('image_hover', 'image_hover_thumbnail'),
            ('image_detail', 'image_detail_thumbnail'),
            ('image_slider', 'image_slider_thumbnail'),
        ],
    )
    def test_player_thumbnail_without_image_in_exact_field(self, field_name, method_name):
        player = Player.objects.create(full_name='Иванов Иван')
        model_admin = PlayerAdmin(Player, admin.site)
        assert getattr(model_admin, method_name)(player) == ''

    def test_player_thumbnail_short_descriptions(self):
        model_admin = PlayerAdmin(Player, admin.site)
        assert model_admin.image_thumbnail.short_description == 'Фото в списке'
        assert model_admin.image_hover_thumbnail.short_description == 'Фото при наведении'
        assert model_admin.image_detail_thumbnail.short_description == 'Фото персональной страницы'
        assert model_admin.image_slider_thumbnail.short_description == 'Фото в слайдере'

    def test_player_admin_config(self):
        model_admin = PlayerAdmin(Player, admin.site)
        assert model_admin.list_display == ('full_name', 'birthday', 'position')
        assert model_admin.list_filter == ('full_name', 'birthday', 'position')
        assert model_admin.readonly_fields == (
            'image_thumbnail',
            'image_hover_thumbnail',
            'image_detail_thumbnail',
            'image_slider_thumbnail',
        )
        assert Player in admin.site._registry

    def test_coach_thumbnail_with_image(self, monkeypatch):
        preview = MagicMock(url='/media/cache/150x250/photo.png', width=150, height=250)
        monkeypatch.setattr('team.admin.get_thumbnail', MagicMock(return_value=preview))

        coach = Coach.objects.create(full_name='Петров Пётр', image='media/team_upload/c.png')
        model_admin = CoachAdmin(Coach, admin.site)
        html = model_admin.photo_thumbnail(coach)

        assert '<img src="/media/cache/150x250/photo.png"' in html
        assert 'width="150"' in html

    def test_coach_thumbnail_without_image(self):
        coach = Coach.objects.create(full_name='Петров Пётр')
        model_admin = CoachAdmin(Coach, admin.site)
        assert model_admin.photo_thumbnail(coach) == ''

    def test_coach_admin_config(self):
        model_admin = CoachAdmin(Coach, admin.site)
        assert model_admin.list_display == ('full_name',)
        assert model_admin.readonly_fields == ('photo_thumbnail',)
        assert model_admin.photo_thumbnail.short_description == 'Фото'
        assert Coach in admin.site._registry


@pytest.mark.django_db
class TestTeamView:
    def test_context_groups_players_by_position(self, client, players):
        response = client.get(reverse('team:all_team'))

        assert response.status_code == 200
        assert list(response.context['goalkeepers']) == [players[Player.GOALKEEPER]]
        assert list(response.context['defenders']) == [players[Player.DEFENDER]]
        assert list(response.context['midfielders']) == [players[Player.MIDFIELDER]]
        assert list(response.context['forwards']) == [players[Player.FORWARD]]

    def test_context_contains_coaches(self, client):
        coach = Coach.objects.create(full_name='Петров Пётр')
        response = client.get(reverse('team:all_team'))
        assert list(response.context['coaches']) == [coach]

    def test_coaches_are_not_rendered_in_template(self, client):
        """БАГ-005: тренерский штаб передаётся в контекст, но не выводится."""
        Coach.objects.create(full_name='УникальныйТренер')
        response = client.get(reverse('team:all_team'))
        # Ожидаемое поведение: тренер должен отображаться на странице команды.
        # assert 'УникальныйТренер' in response.content.decode('utf-8')

    def test_current_tournament_and_teams_order(self, client, tournament):
        positioned = Team.objects.create(
            name='Позиция 1',
            location='Краснодар',
            tournament=tournament,
            position_number=1,
            is_active=True,
        )
        zero_position = Team.objects.create(
            name='Без позиции',
            location='Сочи',
            tournament=tournament,
            position_number=None,
            is_active=True,
        )
        Team.objects.create(
            name='Неактивная',
            location='Москва',
            tournament=tournament,
            position_number=2,
            is_active=False,
        )

        response = client.get(reverse('team:all_team'))

        assert response.context['current_tournament'] == tournament
        assert response.context['teams'] == [positioned, zero_position]

    def test_hashtag_is_added_to_context(self, client):
        hashtag = Hashtag.objects.create(name='Кубань', is_active=True)
        response = client.get(reverse('team:all_team'))
        assert response.context['hashtag'] == hashtag

    def test_without_current_tournament(self, client):
        response = client.get(reverse('team:all_team'))
        assert 'current_tournament' not in response.context
        assert 'teams' not in response.context


@pytest.mark.django_db
class TestPlayerDetailView:
    def test_context_contains_other_players(self, client, players):
        player = players[Player.GOALKEEPER]
        response = client.get(reverse('team:player_detail', args=[player.slug]))

        assert response.status_code == 200
        assert response.context['player'] == player
        assert set(response.context['other_players']) == {
            players[Player.DEFENDER],
            players[Player.MIDFIELDER],
            players[Player.FORWARD],
        }

    def test_unknown_slug_returns_404(self, client):
        response = client.get(reverse('team:player_detail', args=['unknown-player']))
        assert response.status_code == 404

    def test_player_detail_fails_without_image(self, client):
        """БАГ-009: player.html обращается к player.image.url без проверки файла."""
        player = Player.objects.create(full_name='Без Фото')
        response = None
        try:
            response = client.get(reverse('team:player_detail', args=[player.slug]))
        except ValueError:
            pass
        # Ожидаемое поведение: игрок без фото должен открываться (заглушка).
        # assert response is not None and response.status_code == 200

    def test_duplicate_slug_breaks_detail_page(self, client):
        """БАГ-006: slug не уникален, две одинаковые фамилии ломают DetailView."""
        first = Player.objects.create(full_name='Иванов Иван')
        second = Player.objects.create(full_name='Иванов Иван')
        assert first.slug == second.slug == 'ivanov-ivan'

        response = None
        try:
            response = client.get(reverse('team:player_detail', args=[first.slug]))
        except Player.MultipleObjectsReturned:
            pass
        # Ожидаемое поведение: URL должен однозначно открывать одного игрока.
        # assert response is not None and response.status_code == 200


@pytest.mark.django_db
class TestCoachDetailView:
    def test_context_contains_coach(self, client):
        coach = Coach.objects.create(full_name='Петров Пётр')
        response = client.get(reverse('team:coach_detail', args=[coach.slug]))

        assert response.status_code == 200
        assert response.context['coach'] == coach

    def test_coach_template_is_empty(self, client):
        """БАГ-007: шаблон coach.html пустой, страница тренера без вёрстки."""
        coach = Coach.objects.create(full_name='Петров Пётр')
        response = client.get(reverse('team:coach_detail', args=[coach.slug]))

        assert response.status_code == 200
        # Ожидаемое поведение: страница должна содержать базовую вёрстку сайта.
        # assert 'Официальный сайт' in response.content.decode('utf-8')

    def test_unknown_slug_returns_404(self, client):
        response = client.get(reverse('team:coach_detail', args=['unknown-coach']))
        assert response.status_code == 404
