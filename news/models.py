from sorl.thumbnail import ImageField
from transliterate import translit
from ckeditor_uploader.fields import RichTextUploadingField

from django.db import models
from django.utils.text import slugify


class BaseNews(models.Model):
    """
    Абстрактная родительская модель для новостей
    """
    title = models.CharField('Заголовок', max_length=200)
    date_pub = models.DateTimeField('Дата публикации')
    news_text = RichTextUploadingField('Полный текст',
                                        blank=True,
                                        null=True,
                                        config_name='default',
                                        external_plugin_resources=[(
                                            'youtube',
                                            '/static/ckeditor_plugins/youtube/youtube/',
                                            'plugin.js',
                                        )],
                                        )
    published = models.BooleanField('Опубликовать', default=False)
    slug = models.SlugField('Ссылка', max_length=200, null=True, blank=True, unique=True)

    class Meta:
        abstract = True
        ordering = ('-date_pub',)

    def __str__(self):
        return self.title


class NewsHashTag(models.Model):
    """Модель хештэга для новости"""
    text = models.CharField('Хештэг', max_length=20)
    # news = models.ManyToManyField(News, null=True, blank=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Хештэг для новости'
        verbose_name_plural = 'Хештэги для новостей'
        ordering = ('text',)


class News(BaseNews):
    CENTER, LEFT, RIGHT, TOP, BOTTOM = range(5)
    CROP_CHOICES = (
        (CENTER, 'По центру'),
        (LEFT, 'Слева'),
        (RIGHT, 'Справа'),
        (TOP, 'Сверху'),
        (BOTTOM, 'Снизу')
    )

    is_periodic = models.BooleanField('Опубликовать по времени', default=False)
    image = ImageField(
        'Загрузить главное фото',
        default='',
        null=None,
        blank=False,
        upload_to='media/news_upload',
        help_text='Размер фото 750x400'
    )
    crop_image = models.PositiveSmallIntegerField('Фокус на главном фото', choices=CROP_CHOICES, default=CENTER)
    hashtags = models.ManyToManyField(NewsHashTag, verbose_name='Хештэги', null=True, blank=True,  related_name='news')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ('-date_pub',)

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
