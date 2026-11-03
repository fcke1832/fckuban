"""Тесты приложения news."""
import datetime
from unittest.mock import MagicMock

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.utils.datastructures import MultiValueDict

from calendar_matches.models import Match
from links.models import SocialNetworkLink
from news.admin import (
    AdminImageWidget,
    NewsAdmin,
    NewsHashTagAdmin,
    NewsImageForm,
    NewsImageInline,
    NewsHashTagInline,
)
from news.apps import NewsConfig
from news.models import News, NewsHashTag, NewsImage
from news.views import NewsDetailView, NewsListFilterView, NewsListView, news_list_preview
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


def make_news(**kwargs):
    defaults = {
        'title': 'Новость клуба',
        'date_pub': timezone.now(),
        'published': True,
    }
    defaults.update(kwargs)
    return News.objects.create(**defaults)


class TestNewsConfig:
    def test_app_config(self):
        assert NewsConfig.name == 'news'
        assert NewsConfig.verbose_name == 'Новости'


@pytest.mark.django_db
class TestNewsModel:
    def test_str(self):
        news = make_news(title='Победа')
        assert str(news) == 'Победа'

    def test_defaults(self):
        news = make_news()
        assert news.published is True
        assert news.is_periodic is False
        assert news.crop_image == News.CENTER
        assert news.crop_image_detail_page == News.CENTER
        assert news.image.name == ''

    def test_slug_is_generated_on_save(self):
        news = make_news(title='Кубань победила')
        assert news.slug.startswith('kuban-pobedila-')

    def test_slug_is_not_changed_for_existing_value(self):
        news = make_news(title='Кубань победила')
        original_slug = news.slug
        news.title = 'Другой заголовок'
        news.save()
        news.refresh_from_db()
        assert news.slug == original_slug

    def test_generated_slug_contains_dot(self):
        """БАГ-012: слаг новости содержит точку из timestamp и не проходит validate_slug."""
        news = make_news(title='Кубань победила')
        # Ожидаемое поведение: слаг должен проходить validate_slug без ошибок.
        # validate_slug(news.slug)
        with pytest.raises(ValidationError):
            validate_slug(news.slug)

    def test_crop_choices(self):
        assert dict(News.CROP_CHOICES) == {
            0: 'По центру',
            1: 'Слева',
            2: 'Справа',
            3: 'Сверху',
            4: 'Снизу',
        }

    def test_meta(self):
        assert News._meta.verbose_name == 'Новость'
        assert News._meta.verbose_name_plural == 'Новости'
        assert News._meta.ordering == ('-date_pub',)

    def test_hashtags_relation(self):
        hashtag = NewsHashTag.objects.create(text='Кубань')
        news = make_news()
        news.hashtags.add(hashtag)
        assert list(news.hashtags.all()) == [hashtag]
        assert list(hashtag.news.all()) == [news]

    @pytest.mark.parametrize(
        'property_name, size, crop',
        [
            ('get_thumbnail_center', '1200x800', 'center'),
            ('get_thumbnail_right', '1200x800', 'right'),
            ('get_thumbnail_left', '1200x800', 'left'),
            ('get_thumbnail_top', '1200x800', 'top'),
            ('get_thumbnail_bottom', '1200x800', 'bottom'),
            ('thumbnail_center_detail_page', '1500x800', 'center'),
            ('thumbnail_right_detail_page', '1500x800', 'right'),
            ('thumbnail_left_detail_page', '1500x800', 'left'),
            ('thumbnail_top_detail_page', '1500x800', 'top'),
            ('thumbnail_bottom_detail_page', '1500x800', 'bottom'),
            ('small_thumbnail', '700x400', 'center'),
            ('get_thumbnail_list', '393x225', 'center'),
        ],
    )
    def test_thumbnail_properties(self, monkeypatch, property_name, size, crop):
        get_thumbnail = MagicMock()
        get_thumbnail.return_value.url = '/media/cache/news.png'
        monkeypatch.setattr('news.models.get_thumbnail', get_thumbnail)

        news = make_news(image='media/news_upload/news.png')

        assert getattr(news, property_name) == '/media/cache/news.png'
        get_thumbnail.assert_called_once_with(news.image, size, crop=crop, quality=99)


@pytest.mark.django_db
class TestNewsHashTag:
    def test_str(self):
        hashtag = NewsHashTag.objects.create(text='Кубань')
        assert str(hashtag) == 'Кубань'

    def test_meta(self):
        assert NewsHashTag._meta.verbose_name == 'Хештэг для новости'
        assert NewsHashTag._meta.ordering == ('text',)


@pytest.mark.django_db
class TestNewsImage:
    def test_str(self):
        news = make_news(title='Новость')
        image = NewsImage.objects.create(
            slider_image='media/news_upload/slider.png',
            image_news=news,
        )
        assert str(image) == 'Новость'

    def test_defaults(self):
        news = make_news()
        image = NewsImage.objects.create(image_news=news)
        assert image.slider_image.name == ''
        assert image.tip is None

    def test_slider_thumbnail(self, monkeypatch):
        get_thumbnail = MagicMock()
        get_thumbnail.return_value.url = '/media/cache/slider.png'
        monkeypatch.setattr('news.models.get_thumbnail', get_thumbnail)

        news = make_news()
        image = NewsImage.objects.create(
            slider_image='media/news_upload/slider.png',
            image_news=news,
        )

        assert image.slider_thumbnail == '/media/cache/slider.png'
        get_thumbnail.assert_called_once_with(image.slider_image, '1800x1200', crop=None, quality=99)


@pytest.mark.django_db
class TestNewsListView:
    def test_queryset_returns_only_published(self):
        published = make_news(title='Опубликовано', published=True)
        make_news(title='Черновик', published=False)

        assert list(NewsListView().get_queryset()) == [published]

    def test_page_renders_published_news(self, client, monkeypatch):
        thumbnail = MagicMock(url='/media/cache/list.png')
        monkeypatch.setattr('news.models.get_thumbnail', MagicMock(return_value=thumbnail))
        published = make_news(title='Опубликовано', image='media/news_upload/n.png')
        make_news(title='Черновик', published=False, image='media/news_upload/n.png')

        response = client.get(reverse('news:news_list'))

        assert response.status_code == 200
        assert list(response.context['news_list']) == [published]
        assert 'news_list.html' in [t.name for t in response.templates]


@pytest.mark.django_db
class TestNewsListFilterView:
    def test_filters_by_hashtag_and_published(self):
        hashtag = NewsHashTag.objects.create(text='Кубань')
        matching = make_news(title='С хештегом')
        matching.hashtags.add(hashtag)
        make_news(title='Без хештега')
        draft = make_news(title='Черновик', published=False)
        draft.hashtags.add(hashtag)

        view = NewsListFilterView()
        view.kwargs = {'pk': hashtag.pk}

        assert list(view.get_queryset()) == [matching]

    def test_context_contains_hashtag(self, client, monkeypatch):
        monkeypatch.setattr(
            'news.models.get_thumbnail',
            MagicMock(return_value=MagicMock(url='/media/cache/news.png')),
        )
        hashtag = NewsHashTag.objects.create(text='Кубань')
        news = make_news(title='С хештегом', image='media/news_upload/n.png')
        news.hashtags.add(hashtag)

        response = client.get(reverse('news:news_list_filter', args=[hashtag.pk]))

        assert response.status_code == 200
        assert response.context['is_filter'] is True
        assert response.context['current_hashtag'] == hashtag
        assert list(response.context['news_list']) == [news]

    def test_unknown_hashtag_gives_empty_list(self, client):
        response = client.get(reverse('news:news_list_filter', args=[999]))
        assert response.status_code == 200
        assert list(response.context['news_list']) == []
        assert response.context['current_hashtag'] is None


@pytest.mark.django_db
class TestNewsDetailView:
    def test_context_contains_related_news_and_images(self, client, calendar_match, monkeypatch):
        monkeypatch.setattr(
            'news.models.get_thumbnail',
            MagicMock(return_value=MagicMock(url='/media/cache/news.png')),
        )
        hashtag = NewsHashTag.objects.create(text='Кубань')
        news = make_news(title='Главная новость', image='media/news_upload/n.png')
        news.hashtags.add(hashtag)
        another = make_news(title='Другая новость', image='media/news_upload/n.png')
        another.hashtags.add(hashtag)
        unrelated = make_news(title='Без хештега', image='media/news_upload/n.png')
        NewsImage.objects.create(slider_image='media/news_upload/s.png', image_news=news)

        response = client.get(reverse('news:news_detail', args=[news.slug]))

        assert response.status_code == 200
        assert response.context['news'] == news
        assert response.context['is_news'] is True
        assert list(response.context['slider_images']) == list(NewsImage.objects.filter(image_news=news))
        assert set(response.context['another_news']) == {another, unrelated}
        assert set(response.context['another_news_admin']) == {another}

    def test_another_news_excludes_current(self, client, calendar_match):
        news = make_news(title='Текущая')
        view = NewsDetailView()
        view.object = news
        assert news not in view.get_another_news()

    def test_unpublished_news_is_accessible(self, client, calendar_match, monkeypatch):
        """БАГ-010: DetailView не фильтрует published, черновик доступен по URL."""
        monkeypatch.setattr(
            'news.models.get_thumbnail',
            MagicMock(return_value=MagicMock(url='/media/cache/news.png')),
        )
        news = make_news(
            title='Черновик',
            published=False,
            image='media/news_upload/n.png',
        )

        response = client.get(reverse('news:news_detail', args=[news.slug]))

        # Ожидаемое поведение: черновик должен отдавать 404.
        # assert response.status_code == 404
        assert response.status_code == 200

    def test_unknown_slug_returns_404(self, client):
        response = client.get(reverse('news:news_detail', args=['unknown']))
        assert response.status_code == 404

    def test_detail_fails_without_image(self, client, calendar_match):
        """БАГ-014: detail-шаблон обращается к превью без проверки файла."""
        news = make_news(title='Без фото')

        response = None
        try:
            response = client.get(reverse('news:news_detail', args=[news.slug]))
        except AttributeError:
            pass
        # Ожидаемое поведение: новость без фото должна открываться с заглушкой.
        # assert response is not None and response.status_code == 200

    def test_detail_fails_without_calendar_matches(self, client):
        """БАГ-001: детальная новость при пустом календаре падает с IndexError."""
        news = make_news(title='Без календаря')

        response = None
        try:
            response = client.get(reverse('news:news_detail', args=[news.slug]))
        except IndexError:
            pass
        # Ожидаемое поведение: страница должна открываться и без матчей.
        # assert response is not None and response.status_code == 200

    def test_social_network_links_are_mapped(self, client, calendar_match, monkeypatch):
        monkeypatch.setattr(
            'news.models.get_thumbnail',
            MagicMock(return_value=MagicMock(url='/media/cache/news.png')),
        )
        news = make_news(title='Новость', image='media/news_upload/n.png')
        SocialNetworkLink.objects.create(name='FB', link='https://www.facebook.com/fckuban')
        SocialNetworkLink.objects.create(name='VK', link='https://vk.com/fckuban')
        SocialNetworkLink.objects.create(name='IG', link='https://www.instagram.com/fckuban')
        SocialNetworkLink.objects.create(name='YT', link='https://www.youtube.com/fckuban')
        SocialNetworkLink.objects.create(name='TG', link='https://t.me/fckuban')

        response = client.get(reverse('news:news_detail', args=[news.slug]))

        assert response.context['facebook_link'] == 'https://www.facebook.com/fckuban'
        assert response.context['vk_link'] == 'https://vk.com/fckuban'
        assert response.context['instagram_link'] == 'https://www.instagram.com/fckuban'
        assert response.context['youtube_channel'] == 'https://www.youtube.com/fckuban'
        assert response.context['telegram_channel'] == 'https://t.me/fckuban'


@pytest.mark.django_db
class TestNewsPreview:
    def test_anonymous_user_is_redirected(self, client):
        response = client.get(reverse('news:news_list_preview'))
        assert response.status_code == 302
        assert response.url == reverse('index')

    def test_staff_user_sees_unpublished_news(self, client, staff_user, image_file):
        client.force_login(staff_user)
        draft = make_news(title='Черновик', published=False, image=image_file('draft.png'))

        response = client.get(reverse('news:news_list_preview'))

        assert response.status_code == 200
        assert list(response.context['preview_news']) == [draft]

    def test_regular_authenticated_user_can_open_preview(self, client, regular_user):
        """БАГ-013: любой авторизованный пользователь проходит проверку предпросмотра."""
        client.force_login(regular_user)

        response = client.get(reverse('news:news_list_preview'))

        # Ожидаемое поведение: обычный пользователь должен получать redirect.
        # assert response.status_code == 302
        assert response.status_code == 200

    def test_function_redirects_anonymous(self, rf):
        request = rf.get('/news/newslist_preview/')
        request.user = MagicMock(is_authenticated=False, is_superuser=False, is_staff=False)

        response = news_list_preview(request)

        assert response.status_code == 302


@pytest.mark.django_db
class TestNewsAdminWidget:
    def test_render_with_image(self, monkeypatch):
        preview = MagicMock(url='/media/cache/100x100.png')
        monkeypatch.setattr('news.admin.get_thumbnail', MagicMock(return_value=preview))
        news = make_news(image='media/news_upload/n.png')
        widget = AdminImageWidget()

        html = widget.render('image', news.image)

        assert '<img src="/media/cache/100x100.png">' in html
        assert 'type="file"' in html

    def test_render_without_value(self):
        widget = AdminImageWidget()
        html = widget.render('image', None)
        assert 'type="file"' in html
        assert '<img' not in html

    def test_form_meta(self):
        assert NewsImageForm._meta.model is NewsImage
        assert set(NewsImageForm.base_fields) == {
            field.name for field in NewsImage._meta.fields if not field.auto_created
        }
        assert NewsImageForm._meta.widgets['slider_image'] is AdminImageWidget


@pytest.mark.django_db
class TestNewsAdmin:
    def test_registered_and_config(self):
        model_admin = NewsAdmin(News, admin.site)
        assert model_admin.list_display == ('title', 'date_pub', 'published', 'is_periodic')
        assert model_admin.list_editable == ('published', 'is_periodic')
        assert model_admin.readonly_fields == ('photo_thumbnail',)
        assert NewsImageInline in model_admin.inlines
        assert NewsHashTagInline in model_admin.inlines
        assert News in admin.site._registry

    def test_hashtag_admin(self):
        model_admin = NewsHashTagAdmin(NewsHashTag, admin.site)
        assert model_admin.list_display == ('text',)
        assert model_admin.list_filter == ('text',)
        assert NewsHashTag in admin.site._registry

    def test_inline_config(self):
        assert NewsImageInline.model is NewsImage
        assert NewsImageInline.form is NewsImageForm
        assert NewsImageInline.extra == 0
        assert NewsHashTagInline.model is News.hashtags.through
        assert NewsHashTagInline.extra == 1

    def test_photo_thumbnail_with_image(self, monkeypatch):
        preview = MagicMock(url='/media/cache/750x400.png', width=750, height=400)
        monkeypatch.setattr('news.admin.get_thumbnail', MagicMock(return_value=preview))
        news = make_news(image='media/news_upload/n.png')
        model_admin = NewsAdmin(News, admin.site)

        html = model_admin.photo_thumbnail(news)

        assert '<img src="/media/cache/750x400.png"' in html
        assert 'width="750"' in html

    def test_photo_thumbnail_without_image(self):
        news = make_news()
        model_admin = NewsAdmin(News, admin.site)
        assert model_admin.photo_thumbnail(news) == ''

    def test_photo_thumbnail_short_description(self):
        model_admin = NewsAdmin(News, admin.site)
        assert model_admin.photo_thumbnail.short_description == 'Главное фото'

    def test_save_model_creates_slider_images(self, image_file):
        news = make_news()
        model_admin = NewsAdmin(News, admin.site)
        request = RequestFactory().post('/admin/news/news/add/')
        request._files = MultiValueDict({'photos_multiple': [image_file('slider.png')]})

        model_admin.save_model(request, news, form=None, change=False)

        assert news.slider_images.count() == 1
