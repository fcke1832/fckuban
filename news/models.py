from sorl.thumbnail import ImageField
from transliterate import translit
from ckeditor.fields import RichTextField

from django.db import models
from django.conf import settings
from django.utils.text import slugify

from fckuban.utils import image_path


class News(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    date_pub = models.DateTimeField('Дата публикации')
    news_text = RichTextField('Полный текст', null=True)
    published = models.BooleanField('Опубликовать', default=False)
    is_periodic = models.BooleanField('Опубликовать по времени', default=False)
    image = ImageField('Загрузить главное фото', default='', null=None, blank=False, upload_to='media/news_upload', help_text='Размер фото 750x400')
    slug = models.SlugField('Ссылка', max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(translit(str(self.title), 'ru', reversed=True))
            q = News.objects.filter(slug=slug).exclude(pk=self.pk)
            if q.count() > 1:
                slug += "-{}".format(self.id)
            self.slug = slug
        super(News, self).save(*args, **kwargs)


class NewsImage(models.Model):
    slider_image = ImageField('Фото для слайдера', default='', null=None, blank=False, upload_to='media/news_upload')
    image_news = models.ForeignKey(News, models.CASCADE, related_name='slider_images')

    class Meta:
        verbose_name = 'Новостное фото'
        verbose_name_plural = 'Новостные фото'
