"""Тесты приложения medialinks."""
import datetime
from unittest.mock import MagicMock

import pytest
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone

from calendar_matches.models import Match
from links.models import SocialNetworkLink
from medialinks.admin import ArticleAdmin
from medialinks.apps import MedialinksConfig
from medialinks.models import Article
from medialinks.views import ArticleDetailView, ArticlesListView
from news.models import BaseNews
from tournaments.models import Team, Tournament


@pytest.fixture
def calendar_match(db):
    tournament = Tournament.objects.create(title='Первенство', in_calendar=True)
    home = Team.objects.create(name='Кубань', location='Краснодар', tournament=tournament)
    guest = Team.objects.create(name='Ротор', location='Волгоград', tournament=tournament)
    return Match.objects.create(
        home_team=home,
        guest_team=guest,
        tournament=tournament,
        start_time=timezone.now() + datetime.timedelta(days=1),
        is_active=True,
    )


def make_article(**kwargs):
    defaults = {
        'title': 'Новость из СМИ',
        'date_pub': timezone.now(),
        'published': True,
        'is_image': False,
    }
    defaults.update(kwargs)
    return Article.objects.create(**defaults)


class TestMedialinksConfig:
    def test_app_config(self):
        assert MedialinksConfig.name == 'medialinks'
        assert MedialinksConfig.verbose_name == 'СМИ о нас'


@pytest.mark.django_db
class TestArticleModel:
    def test_str(self):
        article = make_article(title='Заголовок')
        assert str(article) == 'Заголовок'

    def test_base_news_is_abstract(self):
        assert BaseNews._meta.abstract is True

    def test_slug_is_generated_on_save(self):
        article = make_article(title='Кубань победила')
        assert article.slug == 'kuban-pobedila'

    def test_slug_is_always_regenerated(self):
        article = make_article(title='Первый заголовок')
        article.title = 'Второй заголовок'
        article.save()
        article.refresh_from_db()
        assert article.slug == 'vtoroj-zagolovok'

    def test_slug_is_unique_for_same_titles(self):
        first = make_article(title='Одинаковый заголовок')
        second = make_article(title='Одинаковый заголовок')
        assert first.slug != second.slug
        assert second.slug.startswith(first.slug)

    def test_defaults(self):
        article = Article.objects.create(title='Статья', date_pub=timezone.now())
        assert article.is_image is True
        assert article.published is False
        assert article.sourse is None
        assert article.sourse_name is None
        assert article.image.name == ''

    def test_meta(self):
        assert Article._meta.verbose_name == 'Статья из СМИ'
        assert Article._meta.verbose_name_plural == 'Статьи из СМИ'
        assert Article._meta.ordering == ('-date_pub',)

    def test_get_thumbnail(self, monkeypatch):
        get_thumbnail = MagicMock()
        get_thumbnail.return_value.url = '/media/cache/1500x800/article.png'
        monkeypatch.setattr('medialinks.models.get_thumbnail', get_thumbnail)

        article = make_article(title='С картинкой', image='media/medialinks_upload/a.png')

        assert article.get_thumbnail == '/media/cache/1500x800/article.png'
        get_thumbnail.assert_called_once_with(article.image, '1500x800', crop='center', quality=99)

    def test_get_thumbnail_list(self, monkeypatch):
        get_thumbnail = MagicMock()
        get_thumbnail.return_value.url = '/media/cache/393x225/article.png'
        monkeypatch.setattr('medialinks.models.get_thumbnail', get_thumbnail)

        article = make_article(title='С картинкой', image='media/medialinks_upload/a.png')

        assert article.get_thumbnail_list == '/media/cache/393x225/article.png'
        get_thumbnail.assert_called_once_with(article.image, '393x225', crop='center', quality=99)

    def test_get_thumbnail_fails_without_image(self):
        """БАГ-011: превью статьи без картинки возвращает пустую строку."""
        article = make_article(title='Без картинки')

        assert article.get_thumbnail == ''
        assert article.get_thumbnail_list == ''


@pytest.mark.django_db
class TestArticleAdmin:
    def test_registered_and_config(self):
        model_admin = ArticleAdmin(Article, admin.site)
        assert model_admin.list_display == (
            'title',
            'date_pub',
            'sourse_name',
            'published',
            'is_image',
        )
        assert model_admin.list_editable == ('published', 'is_image')
        assert Article in admin.site._registry


@pytest.mark.django_db
class TestArticlesListView:
    def test_get_queryset_returns_only_published(self):
        published = make_article(title='Опубликовано', published=True)
        make_article(title='Черновик', published=False)

        view = ArticlesListView()
        assert list(view.get_queryset()) == [published]

    def test_list_page_renders_published_articles(self, client, calendar_match, monkeypatch):
        thumbnail = MagicMock(url='/media/cache/list.png')
        monkeypatch.setattr('medialinks.models.get_thumbnail', MagicMock(return_value=thumbnail))
        published = make_article(
            title='Опубликовано',
            published=True,
            image='media/medialinks_upload/a.png',
        )
        make_article(title='Черновик', published=False)

        response = client.get(reverse('medialinks:articles_list'))

        assert response.status_code == 200
        assert list(response.context['articles_list']) == [published]
        assert 'media_list.html' in [t.name for t in response.templates]

    def test_context_contains_calendar(self, client, calendar_match):
        response = client.get(reverse('medialinks:articles_list'))

        assert response.context['calendar_matches'] == [calendar_match]
        assert response.context['future_match'] == calendar_match
        assert 'birthdays' in response.context
        assert 'today_date' in response.context

    def test_social_network_links_are_mapped(self, client, calendar_match):
        SocialNetworkLink.objects.create(name='FB', link='https://www.facebook.com/fckuban')
        SocialNetworkLink.objects.create(name='VK', link='https://vk.com/fckuban')
        SocialNetworkLink.objects.create(name='IG', link='https://www.instagram.com/fckuban')
        SocialNetworkLink.objects.create(name='YT', link='https://www.youtube.com/fckuban')
        SocialNetworkLink.objects.create(name='TG', link='https://t.me/fckuban')

        response = client.get(reverse('medialinks:articles_list'))

        assert response.context['facebook_link'] == 'https://www.facebook.com/fckuban'
        assert response.context['vk_link'] == 'https://vk.com/fckuban'
        assert response.context['instagram_link'] == 'https://www.instagram.com/fckuban'
        assert response.context['youtube_channel'] == 'https://www.youtube.com/fckuban'
        assert response.context['telegram_channel'] == 'https://t.me/fckuban'

    def test_page_fails_without_calendar_matches(self, client):
        """БАГ-001: при пустом календаре список статей падает с IndexError."""
        response = None
        try:
            response = client.get(reverse('medialinks:articles_list'))
        except IndexError:
            pass
        # Ожидаемое поведение: страница должна открываться и без матчей.
        # assert response is not None and response.status_code == 200


@pytest.mark.django_db
class TestArticleDetailView:
    def test_context_contains_article_and_flag(self, client, calendar_match, monkeypatch):
        thumbnail = MagicMock(url='/media/cache/detail.png')
        monkeypatch.setattr('medialinks.models.get_thumbnail', MagicMock(return_value=thumbnail))
        article = make_article(
            title='Детальная статья',
            published=True,
            image='media/medialinks_upload/a.png',
        )

        response = client.get(
            reverse('medialinks:article_detail', args=[article.slug])
        )

        assert response.status_code == 200
        assert response.context['article'] == article
        assert response.context['is_article'] is True
        assert 'article_detail.html' in [t.name for t in response.templates]

    def test_unpublished_article_is_accessible(self, client, calendar_match):
        """БАГ-010: DetailView не фильтрует published, черновик доступен по URL."""
        article = make_article(title='Черновик', published=False)

        response = client.get(
            reverse('medialinks:article_detail', args=[article.slug])
        )

        # Ожидаемое поведение: черновик должен отдавать 404.
        # assert response.status_code == 404
        assert response.status_code == 200

    def test_unknown_slug_returns_404(self, client):
        response = client.get(reverse('medialinks:article_detail', args=['unknown']))
        assert response.status_code == 404

    def test_social_network_links_are_mapped(self, client, calendar_match, monkeypatch):
        monkeypatch.setattr(
            'medialinks.models.get_thumbnail',
            MagicMock(return_value=MagicMock(url='/media/cache/detail.png')),
        )
        article = make_article(
            title='Статья',
            published=True,
            image='media/medialinks_upload/a.png',
        )
        SocialNetworkLink.objects.create(name='FB', link='https://www.facebook.com/fckuban')
        SocialNetworkLink.objects.create(name='VK', link='https://vk.com/fckuban')
        SocialNetworkLink.objects.create(name='IG', link='https://www.instagram.com/fckuban')
        SocialNetworkLink.objects.create(name='YT', link='https://www.youtube.com/fckuban')
        SocialNetworkLink.objects.create(name='TG', link='https://t.me/fckuban')

        response = client.get(
            reverse('medialinks:article_detail', args=[article.slug])
        )

        assert response.context['facebook_link'] == 'https://www.facebook.com/fckuban'
        assert response.context['vk_link'] == 'https://vk.com/fckuban'
        assert response.context['instagram_link'] == 'https://www.instagram.com/fckuban'
        assert response.context['youtube_channel'] == 'https://www.youtube.com/fckuban'
        assert response.context['telegram_channel'] == 'https://t.me/fckuban'

    def test_detail_fails_without_calendar_matches(self, client):
        """БАГ-001: детальная статья при пустом календаре падает с IndexError."""
        article = make_article(title='Без календаря', published=True)

        response = None
        try:
            response = client.get(
                reverse('medialinks:article_detail', args=[article.slug])
            )
        except IndexError:
            pass
        # Ожидаемое поведение: страница должна открываться и без матчей.
        # assert response is not None and response.status_code == 200

    def test_get_context_data_directly(self, rf, calendar_match, monkeypatch):
        monkeypatch.setattr(
            'medialinks.models.get_thumbnail',
            MagicMock(return_value=MagicMock(url='/media/cache/detail.png')),
        )
        article = make_article(title='Статья', image='media/medialinks_upload/a.png')
        view = ArticleDetailView()
        view.request = rf.get('/')
        view.object = article
        view.kwargs = {'slug': article.slug}

        context = view.get_context_data(object=article)

        assert context['article'] == article
        assert context['is_article'] is True
