from sorl.thumbnail import ImageField, get_thumbnail
from transliterate import translit
from random import getrandbits


from django.db import models
from django.utils.text import slugify

from news.models import BaseNews


class Article(BaseNews):
    """
    Модель статьи из сторонних СМИ
    """

    image = ImageField(
        "Превью фото",
        default="",
        null=True,
        blank=True,
        upload_to="media/medialinks_upload",
    )
    is_image = models.BooleanField("Фото в новости", default=True)
    sourse = models.URLField("Ссылка на источник", null=True, blank=True)
    sourse_name = models.CharField(
        "Название источника статьи", max_length=200, null=True, blank=True
    )

    class Meta:
        verbose_name = "Статья из СМИ"
        verbose_name_plural = "Статьи из СМИ"
        ordering = ("-date_pub",)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(translit(str(self.title), "ru", reversed=True))
            exists_slug = Article.objects.filter(slug=slug).exclude(pk=self.pk).exists()
            while exists_slug:
                slug = "{}-{}".format(slug, getrandbits(16))
                exists_slug = (
                    Article.objects.filter(slug=slug).exclude(pk=self.pk).exists()
                )
            self.slug = slug
        super(Article, self).save(*args, **kwargs)

    @property
    def get_thumbnail(self, size="1500x800", crop="center"):
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def get_thumbnail_list(self, size="393x225", crop="center"):
        return get_thumbnail(self.image, size, crop=crop, quality=99).url
