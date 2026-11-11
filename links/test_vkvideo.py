"""Тесты модели VKVideo для страницы «Видео»."""

from unittest.mock import MagicMock

import pytest
from django.contrib import admin

from links.models import VKVideo


@pytest.mark.django_db
class TestVKVideoModel:
    def test_str_returns_title(self):
        video = VKVideo(title="Гол сезона", link="https://vk.com/video-1_2")
        assert str(video) == "Гол сезона"

    def test_defaults(self):
        video = VKVideo(title="Видео", link="https://vk.com/video-1_2")
        assert video.is_published is True
        assert video.on_main is False

    @pytest.mark.parametrize(
        "link, expected",
        [
            (
                "https://vk.com/video-123456_789012",
                "https://vk.com/video_ext.php?oid=-123456&id=789012",
            ),
            (
                "https://vkvideo.ru/video-123_456",
                "https://vk.com/video_ext.php?oid=-123&id=456",
            ),
            (
                "https://vk.com/video?z=video-5_6",
                "https://vk.com/video_ext.php?oid=-5&id=6",
            ),
            (
                "https://vk.com/video_ext.php?oid=-1&id=2&hash=abc",
                "https://vk.com/video_ext.php?oid=-1&id=2&hash=abc",
            ),
            ("https://example.com/video", ""),
        ],
    )
    def test_embed_url(self, link, expected):
        video = VKVideo(title="Видео", link=link)
        assert video.embed_url == expected

    def test_embed_url_without_match(self):
        video = VKVideo(title="Видео", link="https://vk.com/club123")
        assert video.embed_url == ""

    def test_preview_thumbnail_is_empty_without_image(self):
        video = VKVideo(title="Видео", link="https://vk.com/video-1_2")
        assert video.preview_thumbnail == ""

    def test_preview_thumbnail_uses_sorl(self, monkeypatch):
        monkeypatch.setattr(
            "links.models.get_thumbnail",
            MagicMock(return_value=MagicMock(url="/media/cache/vk.png")),
        )
        video = VKVideo(title="Видео", link="https://vk.com/video-1_2")
        video.preview = "media/vk_video_upload/p.png"

        assert video.preview_thumbnail == "/media/cache/vk.png"

    def test_ordering_is_newest_first(self):
        old = VKVideo.objects.create(title="Старое", link="https://vk.com/video-1_1")
        new = VKVideo.objects.create(title="Новое", link="https://vk.com/video-1_2")

        assert list(VKVideo.objects.all()) == [new, old]

    def test_meta(self):
        assert VKVideo._meta.verbose_name == "Видео VK"
        assert VKVideo._meta.verbose_name_plural == "Видео VK"

    def test_admin_is_registered(self):
        assert VKVideo in admin.site._registry
