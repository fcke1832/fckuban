"""Тесты приложения banner."""
from unittest.mock import MagicMock

import pytest
from django.contrib import admin

import banner.views  # noqa: F401
from banner.admin import BannerAdmin
from banner.apps import BannerConfig
from banner.models import Banner


class TestBannerConfig:
    def test_app_config(self):
        assert BannerConfig.name == 'banner'
        assert BannerConfig.verbose_name == 'Баннер на главной'


@pytest.mark.django_db
class TestBannerModel:
    def test_str_returns_title(self):
        banner = Banner.objects.create(title='Главный баннер', published=True)
        assert str(banner) == 'Главный баннер'

    def test_meta_verbose_names(self):
        assert Banner._meta.verbose_name == 'Баннер'
        assert Banner._meta.verbose_name_plural == 'Баннеры'

    def test_default_published_is_false(self):
        banner = Banner.objects.create(title='Черновик')
        assert banner.published is False

    def test_image_upload_to(self):
        assert Banner._meta.get_field('image').upload_to == 'media/banners'

    def test_create_with_image(self, image_file):
        banner = Banner.objects.create(
            title='Баннер с картинкой',
            published=True,
            image=image_file('banner.png'),
        )
        banner.refresh_from_db()
        assert banner.image.name.startswith('media/banners/')
        assert banner.image.name.endswith('.png')

    def test_title_max_length(self):
        title = 'a' * 100
        banner = Banner.objects.create(title=title)
        assert banner.title == title

    def test_filter_published_banners(self):
        Banner.objects.create(title='Скрытый', published=False)
        published = Banner.objects.create(title='Видимый', published=True)
        assert list(Banner.objects.filter(published=True)) == [published]

    def test_order_by_id_desc(self):
        first = Banner.objects.create(title='Первый')
        second = Banner.objects.create(title='Второй')
        assert list(Banner.objects.order_by('-id')) == [second, first]


@pytest.mark.django_db
class TestBannerGetThumbnail:
    def test_default_size_and_crop(self, monkeypatch):
        get_thumbnail = MagicMock()
        get_thumbnail.return_value.url = '/media/cache/960x790/test.png'
        monkeypatch.setattr('banner.models.get_thumbnail', get_thumbnail)

        banner = Banner.objects.create(title='Баннер', image='media/banners/test.png')

        assert banner.get_thumbnail == '/media/cache/960x790/test.png'
        get_thumbnail.assert_called_once_with(
            banner.image,
            '960x790',
            crop='center',
            quality=99,
        )

    def test_is_property(self, monkeypatch):
        get_thumbnail = MagicMock()
        get_thumbnail.return_value.url = '/media/cache/test.png'
        monkeypatch.setattr('banner.models.get_thumbnail', get_thumbnail)

        banner = Banner.objects.create(title='Баннер', image='media/banners/test.png')

        assert isinstance(Banner.get_thumbnail, property)
        assert banner.get_thumbnail == '/media/cache/test.png'


@pytest.mark.django_db
class TestBannerAdmin:
    def test_registered_and_config(self):
        model_admin = BannerAdmin(Banner, admin.site)
        assert model_admin.list_display == ('title', 'published')
        assert model_admin.list_filter == ('published',)
        assert model_admin.list_editable == ('published',)
        assert Banner in admin.site._registry
        assert isinstance(admin.site._registry[Banner], BannerAdmin)

    def test_show_banner_renders_image_tag(self, monkeypatch):
        preview = MagicMock(url='/media/cache/125/test.png')
        monkeypatch.setattr('banner.admin.get_thumbnail', MagicMock(return_value=preview))

        banner = Banner.objects.create(title='Баннер', image='media/banners/test.png')
        model_admin = BannerAdmin(Banner, admin.site)

        html = model_admin.show_banner(banner)

        assert html == '<img src="/media/cache/125/test.png">'

    def test_show_banner_returns_empty_without_thumbnail(self, monkeypatch):
        monkeypatch.setattr('banner.admin.get_thumbnail', MagicMock(return_value=None))

        banner = Banner.objects.create(title='Баннер', image='media/banners/test.png')
        model_admin = BannerAdmin(Banner, admin.site)

        assert model_admin.show_banner(banner) == ''

    def test_show_banner_allow_tags(self):
        assert BannerAdmin.show_banner.allow_tags is True
