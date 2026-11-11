"""Тесты приложения links."""

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError

import links.views  # noqa: F401
from links.admin import (
    HashtagAdmin,
    MapsLinkAdmin,
    SocialNetworkLinkAdmin,
    YoutubeLinkAdmin,
)
from links.apps import LinksConfig
from links.models import Hashtag, MapsLink, SocialNetworkLink, YoutubeLink


class TestLinksConfig:
    def test_app_config(self):
        assert LinksConfig.name == "links"
        assert LinksConfig.verbose_name == "Ссылки на наши интернет-ресурсы"


@pytest.mark.django_db
class TestYoutubeLink:
    def test_str_returns_description(self):
        link = YoutubeLink.objects.create(
            link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            description="Обзор матча",
        )
        assert str(link) == "Обзор матча"

    def test_defaults(self):
        link = YoutubeLink.objects.create(
            link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            description="Ролик",
        )
        assert link.on_main is False
        assert link.date_pub is not None

    def test_full_clean_accepts_youtube_url(self):
        link = YoutubeLink(
            link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            description="Ролик",
        )
        link.full_clean()

    def test_full_clean_rejects_invalid_url(self):
        link = YoutubeLink(link="not-a-url", description="Ролик")
        with pytest.raises(ValidationError) as exc_info:
            link.full_clean()
        assert "link" in exc_info.value.message_dict


@pytest.mark.django_db
class TestSocialNetworkLink:
    def test_str_returns_name(self):
        link = SocialNetworkLink.objects.create(name="VK", link="https://vk.com/fckuban")
        assert str(link) == "VK"

    def test_full_clean_rejects_invalid_url(self):
        link = SocialNetworkLink(name="VK", link="not-a-url")
        with pytest.raises(ValidationError) as exc_info:
            link.full_clean()
        assert "link" in exc_info.value.message_dict


@pytest.mark.django_db
class TestMapsLink:
    def test_str_returns_name(self):
        link = MapsLink.objects.create(name="Стадион", iframe="https://yandex.ru/maps/")
        assert str(link) == "Стадион"

    def test_defaults(self):
        link = MapsLink.objects.create(name="Стадион", iframe="https://yandex.ru/maps/")
        assert link.title == ""
        assert link.is_active is False

    def test_full_clean_rejects_invalid_url(self):
        link = MapsLink(name="Стадион", iframe="<iframe></iframe>")
        with pytest.raises(ValidationError) as exc_info:
            link.full_clean()
        assert "iframe" in exc_info.value.message_dict


@pytest.mark.django_db
class TestHashtag:
    def test_str_returns_name(self):
        hashtag = Hashtag.objects.create(name="Кубань")
        assert str(hashtag) == "Кубань"

    def test_default_is_inactive(self):
        hashtag = Hashtag.objects.create(name="Кубань")
        assert hashtag.is_active is False


@pytest.mark.django_db
class TestLinksAdmin:
    def test_youtube_admin(self):
        model_admin = YoutubeLinkAdmin(YoutubeLink, admin.site)
        assert model_admin.list_display == ("description", "on_main", "date_pub")
        assert model_admin.list_editable == ("on_main",)
        assert model_admin.list_filter == ("on_main", "date_pub")
        assert YoutubeLink in admin.site._registry

    def test_social_network_admin(self):
        model_admin = SocialNetworkLinkAdmin(SocialNetworkLink, admin.site)
        assert model_admin.list_display == ("name", "link")
        assert model_admin.list_editable == ("link",)
        assert model_admin.list_filter == ("name", "link")
        assert SocialNetworkLink in admin.site._registry

    def test_maps_admin(self):
        model_admin = MapsLinkAdmin(MapsLink, admin.site)
        assert model_admin.list_display == ("name", "iframe", "is_active")
        assert model_admin.list_editable == ("iframe", "is_active")
        assert model_admin.list_filter == ("name", "iframe", "is_active")
        assert MapsLink in admin.site._registry

    def test_hashtag_admin(self):
        model_admin = HashtagAdmin(Hashtag, admin.site)
        assert model_admin.list_display == ("name", "is_active")
        assert model_admin.list_editable == ("is_active",)
        assert model_admin.list_filter == ("name", "is_active")
        assert Hashtag in admin.site._registry
