from sorl.thumbnail import ImageField
from transliterate import translit

from django.db import models
from django.utils.text import slugify

from news.models import BaseNews


class Article(BaseNews):
    """
    Модель статьи из сторонних СМИ
    """
    image = ImageField('Превью фото', default='', null=True, blank=True, upload_to='media/medialinks_upload')
    is_image = models.BooleanField('Фото в новости', default=True)
    sourse = models.URLField('Ссылка на источник', null=True, blank=True)
    sourse_name = models.CharField('Название источника статьи', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Статья из СМИ'
        verbose_name_plural = 'Статьи из СМИ'
        ordering = ('-date_pub',)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(translit(str(self.title), 'ru', reversed=True))
            q = Article.objects.filter(slug=slug).exclude(pk=self.pk)
            if q.count() > 1:
                slug += "-{}".format(self.id)
            self.slug = slug
        super(Article, self).save(*args, **kwargs)
