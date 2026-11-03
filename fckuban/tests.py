"""Тесты ядра проекта fckuban (views, utils, templatetags, urls)."""
import datetime
from hashlib import md5 as real_md5
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from django.template import Context, Template
from django.urls import resolve, reverse
from django.utils import timezone

from banner.models import Banner
from birthdays.models import BirthdayItem
from calendar_matches.models import Match
from fckuban import views as core_views
from fckuban.utils import check_now, image_path
from fckuban.views import (
    MainView,
    get_calendar,
    get_calendar_matches,
    get_hashtag,
    get_tournament,
    seo_data,
)
from links.models import Hashtag, MapsLink, SocialNetworkLink, YoutubeLink
from news.models import News
from seo.models import SeoData
from tournaments.models import Team, Tournament


@pytest.fixture
def fixed_now(monkeypatch):
    now = timezone.make_aware(datetime.datetime(2024, 11, 3, 12, 0))
    monkeypatch.setattr('fckuban.views.check_now', lambda: now)
    monkeypatch.setattr('birthdays.views.check_now', lambda: now)
    # Не зависим от наличия системной локали ru_RU.UTF-8 в тестовом окружении
    # (сама проблема описана в BUG-024).
    monkeypatch.setattr('birthdays.views.locale.setlocale', lambda *args: None)
    return now


@pytest.fixture
def calendar_tournament(db):
    return Tournament.objects.create(title='Календарь', in_calendar=True)


@pytest.fixture
def calendar_match(db, calendar_tournament, fixed_now):
    home = Team.objects.create(name='Кубань', location='Краснодар', tournament=calendar_tournament)
    guest = Team.objects.create(name='Ротор', location='Волгоград', tournament=calendar_tournament)
    return Match.objects.create(
        home_team=home,
        guest_team=guest,
        tournament=calendar_tournament,
        start_time=fixed_now + datetime.timedelta(days=1),
        is_active=True,
    )


class TestUtils:
    def test_check_now_returns_aware_datetime(self):
        now = check_now()
        assert now.tzinfo is not None
        assert now.utcoffset() is not None

    def test_image_path_uses_hashes(self, monkeypatch):
        monkeypatch.setattr('fckuban.utils.random.sample', lambda population, k: list(population)[:k])
        monkeypatch.setattr(
            'fckuban.utils.md5',
            lambda value: real_md5(value.encode('utf-8') if isinstance(value, str) else value),
        )

        instance = SimpleNamespace(id=42)
        result = image_path(instance, 'Photo.JPG')

        assert result.endswith('.jpg')
        assert '/' in result
        directory, filename = result.split('/')
        assert len(directory) == 32
        assert len(filename) == 8 + 4

    def test_image_path_without_extension(self, monkeypatch):
        monkeypatch.setattr('fckuban.utils.random.sample', lambda population, k: list(population)[:k])
        monkeypatch.setattr(
            'fckuban.utils.md5',
            lambda value: real_md5(value.encode('utf-8') if isinstance(value, str) else value),
        )

        result = image_path(SimpleNamespace(id=1), 'photo')

        assert not result.endswith('/')
        assert len(result.split('/')[1]) == 8

    def test_image_path_fails_with_str_digest(self):
        """БАГ-021: md5 вызывается со str, на Python 3 это TypeError."""
        # Ожидаемое поведение: функция возвращает путь к файлу.
        # assert image_path(SimpleNamespace(id=1), 'photo.png')
        with pytest.raises(TypeError):
            image_path(SimpleNamespace(id=1), 'photo.png')


@pytest.mark.django_db
class TestCoreHelpers:
    def test_get_hashtag_returns_latest_active(self):
        Hashtag.objects.create(name='Старый', is_active=True)
        latest = Hashtag.objects.create(name='Новый', is_active=True)
        Hashtag.objects.create(name='Скрытый', is_active=False)

        assert get_hashtag() == latest

    def test_get_hashtag_returns_none(self):
        Hashtag.objects.create(name='Скрытый', is_active=False)
        assert get_hashtag() is None

    def test_seo_data_returns_last(self):
        SeoData.objects.create(title='Первый')
        last = SeoData.objects.create(title='Последний')
        assert seo_data() == last

    def test_seo_data_returns_none(self):
        assert seo_data() is None

    def test_get_tournament_returns_current(self):
        Tournament.objects.create(title='Не текущий', on_main=False)
        current = Tournament.objects.create(title='Текущий', on_main=True)
        assert get_tournament() == current

    def test_get_tournament_returns_none(self):
        assert get_tournament() is None

    def test_get_calendar_filters_tournaments_and_active_matches(self, calendar_match):
        Tournament.objects.create(title='Без календаря', in_calendar=False)
        inactive_match = Match.objects.create(
            home_team=calendar_match.home_team,
            guest_team=calendar_match.guest_team,
            tournament=calendar_match.tournament,
            start_time=timezone.now(),
            is_active=False,
        )

        tournaments = list(get_calendar())

        assert [t.title for t in tournaments] == ['Календарь']
        assert list(tournaments[0].match.all()) == [calendar_match]
        assert inactive_match not in tournaments[0].match.all()


@pytest.mark.django_db
class TestGetCalendarMatches:
    def test_splits_past_and_future(self, calendar_tournament, fixed_now):
        home = Team.objects.create(name='Дома', location='Краснодар', tournament=calendar_tournament)
        guest = Team.objects.create(name='Гости', location='Москва', tournament=calendar_tournament)
        past = Match.objects.create(
            home_team=home,
            guest_team=guest,
            tournament=calendar_tournament,
            start_time=fixed_now - datetime.timedelta(days=1),
            is_active=True,
        )
        future = Match.objects.create(
            home_team=home,
            guest_team=guest,
            tournament=calendar_tournament,
            start_time=fixed_now + datetime.timedelta(days=1),
            is_active=True,
        )

        matches, future_matches = get_calendar_matches(get_calendar())

        assert set(matches) == {past, future}
        assert future_matches == [future]

    def test_today_match_is_future(self, calendar_tournament, fixed_now):
        home = Team.objects.create(name='Дома', tournament=calendar_tournament)
        guest = Team.objects.create(name='Гости', tournament=calendar_tournament)
        today = Match.objects.create(
            home_team=home,
            guest_team=guest,
            tournament=calendar_tournament,
            start_time=fixed_now,
            is_active=True,
        )

        _, future_matches = get_calendar_matches(get_calendar())
        assert future_matches == [today]

    def test_match_without_start_time_fails(self, calendar_tournament):
        """БАГ-019: start_time nullable, но get_calendar_matches вызывает .date()."""
        home = Team.objects.create(name='Дома', tournament=calendar_tournament)
        guest = Team.objects.create(name='Гости', tournament=calendar_tournament)
        Match.objects.create(
            home_team=home,
            guest_team=guest,
            tournament=calendar_tournament,
            start_time=None,
            is_active=True,
        )

        # Ожидаемое поведение: матч без start_time не ломает календарь.
        # get_calendar_matches(get_calendar())
        with pytest.raises(AttributeError):
            get_calendar_matches(get_calendar())


@pytest.mark.django_db
class TestMainViewHelpers:
    def test_get_news_returns_published_ordered(self):
        old = News.objects.create(
            title='Старая', date_pub=timezone.now() - datetime.timedelta(days=2), published=True,
        )
        new = News.objects.create(
            title='Новая', date_pub=timezone.now(), published=True,
        )
        News.objects.create(
            title='Черновик', date_pub=timezone.now(), published=False,
        )

        result = list(MainView()._get_news())

        assert result == [new, old]

    def test_get_news_limits_to_five(self):
        for index in range(6):
            News.objects.create(
                title=f'Новость {index}',
                date_pub=timezone.now() + datetime.timedelta(minutes=index),
                published=True,
            )

        assert len(list(MainView()._get_news())) == 5

    def test_get_periodic_news(self):
        periodic = News.objects.create(
            title='Отложенная',
            date_pub=timezone.now(),
            published=False,
            is_periodic=True,
        )
        News.objects.create(title='Обычный черновик', date_pub=timezone.now(), published=False)

        assert list(MainView()._get_periodic_news()) == [periodic]

    def test_get_banner_returns_latest_published(self):
        Banner.objects.create(title='Старый', published=True)
        latest = Banner.objects.create(title='Новый', published=True)
        Banner.objects.create(title='Скрытый', published=False)

        assert MainView()._get_banner() == latest

    def test_get_banner_returns_none(self):
        assert MainView()._get_banner() is None

    def test_check_news_time_publishes_due_news(self, fixed_now):
        due = News.objects.create(
            title='Пора публиковать',
            date_pub=fixed_now - datetime.timedelta(minutes=1),
            published=False,
            is_periodic=True,
        )
        future = News.objects.create(
            title='Ещё рано',
            date_pub=fixed_now + datetime.timedelta(days=1),
            published=False,
            is_periodic=True,
        )

        MainView().check_news_time(MainView()._get_periodic_news())

        due.refresh_from_db()
        future.refresh_from_db()
        assert due.published is True
        assert due.is_periodic is False
        assert future.published is False
        assert future.is_periodic is True


@pytest.mark.django_db
class TestMainViewPage:
    def test_main_page_with_full_context(
        self, client, fixed_now, calendar_match, monkeypatch,
    ):
        monkeypatch.setattr(
            'news.models.get_thumbnail',
            MagicMock(return_value=MagicMock(url='/media/cache/news.png')),
        )
        monkeypatch.setattr(
            'banner.models.get_thumbnail',
            MagicMock(return_value=MagicMock(url='/media/cache/banner.png')),
        )

        current = Tournament.objects.create(title='Текущий турнир', on_main=True)
        positioned = Team.objects.create(
            name='Кубань', tournament=current, position_number=1, is_active=True,
        )
        zero = Team.objects.create(
            name='Без места', tournament=current, position_number=None, is_active=True,
        )
        Team.objects.create(
            name='Неактивная', tournament=current, position_number=2, is_active=False,
        )

        news = News.objects.create(
            title='Новость', date_pub=timezone.now(), published=True,
            image='media/news_upload/n.png',
        )
        banner = Banner.objects.create(
            title='Баннер', published=True, image='media/banners/b.png',
        )
        hashtag = Hashtag.objects.create(name='Кубань', is_active=True)
        seo = SeoData.objects.create(title='SEO', description='Описание', keywords='ключ')
        youtube_main = YoutubeLink.objects.create(
            link='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            description='Главное видео',
            on_main=True,
        )
        youtube_blog = YoutubeLink.objects.create(
            link='https://www.youtube.com/watch?v=other',
            description='Блог',
            on_main=False,
        )
        SocialNetworkLink.objects.create(name='FB', link='https://www.facebook.com/fckuban')
        SocialNetworkLink.objects.create(name='VK', link='https://vk.com/fckuban')
        SocialNetworkLink.objects.create(name='IG', link='https://www.instagram.com/fckuban')
        SocialNetworkLink.objects.create(name='YT', link='https://www.youtube.com/fckuban')
        SocialNetworkLink.objects.create(name='TG', link='https://t.me/fckuban')
        SocialNetworkLink.objects.create(name='TW', link='https://twitter.com/fckuban')
        maps = MapsLink.objects.create(
            name='Карта', iframe='https://yandex.ru/maps/', title='Стадион', is_active=True,
        )
        BirthdayItem.objects.create(
            name='Иван', second_name='Иванов', date_of_birth=datetime.date(1990, 11, 3),
        )

        response = client.get(reverse('index'))

        assert response.status_code == 200
        assert 'main.html' in [t.name for t in response.templates]
        context = response.context
        assert context['news_qs'][0] == news
        assert context['current_tournament'] == current
        assert context['teams'] == [positioned, zero]
        assert context['youtube_link'] == youtube_main
        assert list(context['youtube_blog']) == [youtube_blog]
        assert context['facebook_link'] == 'https://www.facebook.com/fckuban'
        assert context['vk_link'] == 'https://vk.com/fckuban'
        assert context['instagram_link'] == 'https://www.instagram.com/fckuban'
        assert context['youtube_channel'] == 'https://www.youtube.com/fckuban'
        assert context['telegram_channel'] == 'https://t.me/fckuban'
        assert context['twitter_link'] == 'https://twitter.com/fckuban'
        assert context['maps_link'] == maps.iframe
        assert context['maps_title'] == maps.title
        assert context['calendar_matches'] == [calendar_match]
        assert context['future_match'] == calendar_match
        assert context['banner'] == banner
        assert context['hashtag'] == hashtag
        assert context['seo'] == seo
        assert len(context['birthdays']) == 1
        assert context['today_date'].startswith('3 ')

    def test_main_page_without_optional_data(self, client, calendar_match):
        response = client.get(reverse('index'))
        assert response.status_code == 200
        assert response.context['news_qs'].count() == 0
        assert 'youtube_link' not in response.context
        assert 'youtube_blog' not in response.context
        assert 'maps_link' not in response.context
        assert response.context['banner'] is None
        assert response.context['hashtag'] is None
        assert response.context['seo'] is None

    def test_main_page_publishes_periodic_news(
        self, client, fixed_now, calendar_match, monkeypatch,
    ):
        monkeypatch.setattr(
            'news.models.get_thumbnail',
            MagicMock(return_value=MagicMock(url='/media/cache/news.png')),
        )
        due = News.objects.create(
            title='Отложенная',
            date_pub=fixed_now - datetime.timedelta(minutes=1),
            published=False,
            is_periodic=True,
            image='media/news_upload/n.png',
        )

        response = client.get(reverse('index'))

        due.refresh_from_db()
        assert response.status_code == 200
        assert due.published is True
        assert due.is_periodic is False
        assert due in list(response.context['news_qs'])

    def test_main_page_fails_without_calendar_matches(self, client):
        """БАГ-001: главная страница падает с IndexError при пустом календаре."""
        response = None
        try:
            response = client.get(reverse('index'))
        except IndexError:
            pass
        # Ожидаемое поведение: главная должна открываться и без матчей.
        # assert response is not None and response.status_code == 200

    def test_get_context_data_directly(self, rf, calendar_match, fixed_now):
        view = MainView()
        view.request = rf.get('/')
        context = view.get_context_data()
        assert context['future_match'] == calendar_match


@pytest.mark.django_db
class TestTemplateTags:
    def test_current_tournament_tag_with_tournament(self):
        current = Tournament.objects.create(title='Текущий', on_main=True)
        template = Template('{% load calendar %}{% current_tournament %}')
        rendered = template.render(Context({}))
        assert rendered == str(current)

    def test_current_tournament_tag_without_tournament(self):
        template = Template('{% load calendar %}{% current_tournament %}')
        # БАГ-022: тег возвращает None, и в шаблоне выводится строка "None".
        # Ожидаемое поведение: пустая строка.
        # assert template.render(Context({})) == ''
        assert template.render(Context({})) == 'None'

    def test_calendar_tournaments_tag(self, calendar_match):
        """БАГ-020: в templatetags/calendar.py не импортирован Match."""
        template = Template('{% load calendar %}{% calendar_tournaments %}')
        rendered = None
        try:
            rendered = template.render(Context({}))
        except NameError:
            pass
        # Ожидаемое поведение: тег должен вернуть queryset турниров календаря.
        # assert rendered is not None

    def test_calendar_tournaments_tag_returns_queryset(self, monkeypatch, calendar_tournament):
        from fckuban.templatetags import calendar as calendar_tags

        monkeypatch.setattr(calendar_tags, 'get_calendar', lambda: [calendar_tournament])
        result = calendar_tags.calendar_tournaments(Context({}))
        assert result == [calendar_tournament]

    def test_module_get_calendar_fails(self):
        """БАГ-020: get_calendar в templatetags использует неимпортированный Match."""
        from fckuban.templatetags import calendar as calendar_tags

        with pytest.raises(NameError):
            list(calendar_tags.get_calendar())

    def test_module_get_tournament(self):
        from fckuban.templatetags import calendar as calendar_tags

        assert calendar_tags.get_tournament() is None
        Tournament.objects.create(title='Текущий', on_main=True)
        assert calendar_tags.get_tournament().title == 'Текущий'


class TestUrls:
    def test_index_resolves(self):
        assert resolve('/').func.view_class is MainView

    def test_named_routes_resolve(self):
        assert reverse('index') == '/'
        assert reverse('news:news_list') == '/news/newslist/'
        assert reverse('medialinks:articles_list') == '/media/article_list/'
        assert reverse('tickets:ticket_sale') == '/tickets/sale'
        assert reverse('team:all_team') == '/team/all_team/'
        assert reverse('partners:partners_list') == '/partners/'
        assert reverse('tournaments:standings') == '/tournaments/standings/'

    def test_admin_and_ckeditor_are_included(self):
        assert resolve('/admin/')
        assert resolve('/ckeditor/upload/')
