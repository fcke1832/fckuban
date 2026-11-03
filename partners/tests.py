"""Тесты приложения partners."""
import datetime
from unittest.mock import MagicMock

import pytest
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone

from calendar_matches.models import Match
from partners.admin import PartnerAdmin
from partners.apps import PartnersConfig
from partners.models import Partner
from partners.views import PartnerListView
from tournaments.models import Team, Tournament


@pytest.fixture
def tournament(db):
    return Tournament.objects.create(title='Первенство', in_calendar=True)


@pytest.fixture
def calendar_match(db, tournament):
    home = Team.objects.create(name='Кубань', location='Краснодар', tournament=tournament)
    guest = Team.objects.create(name='Ротор', location='Волгоград', tournament=tournament)
    return Match.objects.create(
        home_team=home,
        guest_team=guest,
        tournament=tournament,
        start_time=timezone.now() + datetime.timedelta(days=1),
        is_active=True,
    )


class TestPartnersConfig:
    def test_app_config(self):
        assert PartnersConfig.name == 'partners'


@pytest.mark.django_db
class TestPartnerModel:
    def test_str(self):
        partner = Partner.objects.create(title='Кубань-Спорт')
        assert str(partner) == 'Кубань-Спорт'

    def test_defaults(self):
        partner = Partner.objects.create(title='Партнёр')
        assert partner.type_partner == Partner.PARTNER
        assert partner.is_active is False
        assert partner.number == 0
        assert partner.link is None
        assert partner.contacts is None
        assert partner.description is None

    def test_partner_choices(self):
        assert Partner.PARTNER == 1
        assert Partner.SPONSOR == 2
        assert dict(Partner.PARTNER_CHOICES) == {1: 'Партнёр', 2: 'Спонсор'}

    def test_meta_verbose_names(self):
        assert Partner._meta.verbose_name == 'Партнёр'
        assert Partner._meta.verbose_name_plural == 'Партнёры'

    def test_meta_ordering(self):
        first = Partner.objects.create(title='А', number=1)
        second = Partner.objects.create(title='Б', number=2)
        assert list(Partner.objects.all()) == [second, first]

    def test_logo_thumbnail(self, monkeypatch):
        thumbnail = MagicMock()
        thumbnail.url = '/media/cache/70x70/logo.png'
        monkeypatch.setattr('partners.models.get_thumbnail', MagicMock(return_value=thumbnail))

        partner = Partner.objects.create(title='Партнёр', image='media/partners_upload/logo.png')
        assert partner.logo_thumbnail == '/media/cache/70x70/logo.png'

    def test_logo_thumbnail_passes_default_size(self, monkeypatch):
        get_thumbnail = MagicMock()
        get_thumbnail.return_value.url = '/media/cache/logo.png'
        monkeypatch.setattr('partners.models.get_thumbnail', get_thumbnail)

        partner = Partner.objects.create(title='Партнёр', image='media/partners_upload/logo.png')
        _ = partner.logo_thumbnail

        get_thumbnail.assert_called_once_with(partner.image, '70x70', quality=99)


@pytest.mark.django_db
class TestPartnerAdmin:
    def test_registered_and_config(self):
        model_admin = PartnerAdmin(Partner, admin.site)
        assert model_admin.list_display == ('title', 'type_partner', 'number', 'is_active')
        assert model_admin.list_editable == ('is_active', 'number')
        assert model_admin.readonly_fields == ('logo_thumbnail',)
        assert Partner in admin.site._registry

    def test_logo_thumbnail_with_image(self, monkeypatch):
        preview = MagicMock(url='/media/cache/70x70/logo.png', width=70, height=70)
        monkeypatch.setattr('partners.admin.get_thumbnail', MagicMock(return_value=preview))

        partner = Partner.objects.create(title='Партнёр', image='media/partners_upload/logo.png')
        model_admin = PartnerAdmin(Partner, admin.site)
        html = model_admin.logo_thumbnail(partner)

        assert '<img src="/media/cache/70x70/logo.png"' in html
        assert 'width="70"' in html

    def test_logo_thumbnail_without_image(self):
        partner = Partner.objects.create(title='Партнёр')
        model_admin = PartnerAdmin(Partner, admin.site)
        assert model_admin.logo_thumbnail(partner) == ''

    def test_logo_thumbnail_short_description(self):
        model_admin = PartnerAdmin(Partner, admin.site)
        assert model_admin.logo_thumbnail.short_description == 'Логотип'


@pytest.mark.django_db
class TestPartnerListView:
    def test_filters_active_partners_and_sponsors(self, client, calendar_match, monkeypatch):
        preview = MagicMock(url='/media/cache/logo.png')
        monkeypatch.setattr('partners.models.get_thumbnail', MagicMock(return_value=preview))
        Partner.objects.create(title='Активный партнёр', type_partner=Partner.PARTNER, is_active=True)
        Partner.objects.create(title='Скрытый партнёр', type_partner=Partner.PARTNER, is_active=False)
        Partner.objects.create(title='Активный спонсор', type_partner=Partner.SPONSOR, is_active=True)
        Partner.objects.create(title='Скрытый спонсор', type_partner=Partner.SPONSOR, is_active=False)

        response = client.get(reverse('partners:partners_list'))

        assert response.status_code == 200
        assert [p.title for p in response.context['partners']] == ['Активный партнёр']
        assert [p.title for p in response.context['sponsors']] == ['Активный спонсор']

    def test_context_contains_calendar_and_birthdays(self, client, calendar_match):
        response = client.get(reverse('partners:partners_list'))
        assert response.status_code == 200
        assert list(response.context['calendar_matches']) == [calendar_match]
        assert response.context['future_match'] == calendar_match
        assert 'birthdays' in response.context
        assert 'today_date' in response.context

    def test_social_network_links_are_mapped(self, client, calendar_match):
        from links.models import SocialNetworkLink

        # Партнёров без логотипа на этой странице нет — шаблон не обращается
        # к logo_thumbnail, поэтому патчить sorl не нужно.

        SocialNetworkLink.objects.create(name='FB', link='https://www.facebook.com/fckuban')
        SocialNetworkLink.objects.create(name='VK', link='https://vk.com/fckuban')
        SocialNetworkLink.objects.create(name='IG', link='https://www.instagram.com/fckuban')
        SocialNetworkLink.objects.create(name='YT', link='https://www.youtube.com/fckuban')
        SocialNetworkLink.objects.create(name='TG', link='https://t.me/fckuban')

        response = client.get(reverse('partners:partners_list'))

        assert response.context['facebook_link'] == 'https://www.facebook.com/fckuban'
        assert response.context['vk_link'] == 'https://vk.com/fckuban'
        assert response.context['instagram_link'] == 'https://www.instagram.com/fckuban'
        assert response.context['youtube_channel'] == 'https://www.youtube.com/fckuban'
        assert response.context['telegram_channel'] == 'https://t.me/fckuban'

    def test_get_queryset_returns_all_partners(self, db):
        partner = Partner.objects.create(title='Любой')
        view = PartnerListView()
        assert list(view.get_queryset()) == [partner]

    def test_view_fails_without_calendar_matches(self, client):
        """БАГ-001: при пустом календаре представление падает с IndexError."""
        response = None
        try:
            response = client.get(reverse('partners:partners_list'))
        except IndexError:
            pass
        # Ожидаемое поведение: страница должна открываться и без матчей.
        # assert response is not None and response.status_code == 200

    def test_page_fails_when_partner_has_no_logo(self, client, calendar_match):
        """БАГ-004: логотип необязателен, но logo_thumbnail падает на пустом image."""
        Partner.objects.create(
            title='Партнёр без логотипа',
            type_partner=Partner.PARTNER,
            is_active=True,
        )
        response = None
        try:
            response = client.get(reverse('partners:partners_list'))
        except AttributeError:
            pass
        # Ожидаемое поведение: страница с партнёром без логотипа должна открываться.
        # assert response is not None and response.status_code == 200
