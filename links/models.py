import re
from urllib.parse import urlparse

from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone
from embed_video.fields import EmbedVideoField
from sorl.thumbnail import ImageField, get_thumbnail

VK_VIDEO_PAGE_RE = re.compile(r"video(-?\d+)_(\d+)")
VK_VIDEO_EMBED_URL = "https://vk.com/video_ext.php?oid={oid}&id={video_id}"


class YoutubeLink(models.Model):
    link = EmbedVideoField("Ссылка на Youtube")
    description = models.CharField("Описание ролика", max_length=200)
    on_main = models.BooleanField("На главной", default=False)
    date_pub = models.DateTimeField("Дата публикации", auto_now=True)

    def __str__(self):
        return self.description


class VKVideo(models.Model):
    """Ролик VK Видео для страницы «Видео»."""

    title = models.CharField("Название", max_length=200)
    link = models.URLField(
        "Ссылка на ролик VK Видео",
        max_length=500,
        help_text=(
            "Подойдёт ссылка вида https://vk.com/video-123456_789012, "
            "https://vkvideo.ru/video-123456_789012 или готовая ссылка "
            "https://vk.com/video_ext.php?oid=...&id=...&hash=..."
        ),
    )
    description = models.TextField("Описание", blank=True)
    preview = ImageField(
        "Превью",
        upload_to="media/vk_video_upload",
        blank=True,
        null=True,
        help_text="Необязательно: если пусто, будет заглушка.",
    )
    date_pub = models.DateTimeField("Дата публикации", default=timezone.now)
    is_published = models.BooleanField("Опубликовано", default=True)
    on_main = models.BooleanField("Главное видео", default=False)

    class Meta:
        verbose_name = "Видео VK"
        verbose_name_plural = "Видео VK"
        ordering = ("-date_pub", "-id")

    def __str__(self) -> str:
        return self.title

    @property
    def embed_url(self) -> str:
        """Возвращает URL для iframe VK Видео или пустую строку."""
        if "video_ext.php" in self.link:
            return self.link
        parsed = urlparse(self.link)
        match = VK_VIDEO_PAGE_RE.search(parsed.path) or VK_VIDEO_PAGE_RE.search(parsed.query)
        if not match:
            return ""
        return VK_VIDEO_EMBED_URL.format(oid=match.group(1), video_id=match.group(2))

    @property
    def preview_thumbnail(self) -> str:
        """Возвращает URL превью 800x450 или пустую строку."""
        if not self.preview:
            return ""
        return get_thumbnail(self.preview, "800x450", crop="center").url


class SocialNetworkLink(models.Model):
    name = models.CharField("Название", max_length=30)
    link = models.URLField("Ссылка")

    def __str__(self):
        return self.name


class MapsLink(models.Model):
    name = models.CharField("Название", max_length=30)
    iframe = models.TextField("Ссылка", default="", validators=[URLValidator()])
    title = models.CharField("Заголовок раздела", max_length=100, default="")
    is_active = models.BooleanField("На главной", default=False)

    def __str__(self):
        return self.name


class Hashtag(models.Model):
    name = models.CharField("Хэштег на главной", max_length=30)
    is_active = models.BooleanField("Активный", default=False)

    def __str__(self):
        return self.name
