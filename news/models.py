from django.db import models
from django.conf import settings
from sorl.thumbnail import ImageField

from fckuban.utils import image_path


class News(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    date_pub = models.DateTimeField('Дата публикации')
    news_text = models.TextField('Полный текст', null=True)
    published = models.BooleanField('Опубликовать', default=False)
    image = ImageField('Фото', default='', null=None, blank=False, upload_to='media/news_upload')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
