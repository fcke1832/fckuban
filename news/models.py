from sorl.thumbnail import ImageField, get_thumbnail
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
    crop_image = models.PositiveSmallIntegerField('Выравнивание фото в слайдере на главной странице', choices=CROP_CHOICES, default=CENTER)
    crop_image_detail_page = models.PositiveSmallIntegerField('Выравнивание фото на детальной странице новости', choices=CROP_CHOICES, default=CENTER)
    hashtags = models.ManyToManyField(NewsHashTag, verbose_name='Хештэги', null=True, blank=True,  related_name='news')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ('-date_pub',)

    @property
    def get_thumbnail_center(self, size='1200x800', crop='center'):
        """
        Возвращает preview изображения указанного размера с обрезкой по центру.
        """
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def get_thumbnail_right(self, size='1200x800', crop='right'):
        """
        Возвращает preview изображения указанного размера с обрезкой справа.
        """
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def get_thumbnail_left(self, size='1200x800', crop='left'):
        """
        Возвращает preview изображения указанного размера с обрезкой слева.
        """
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def get_thumbnail_top(self, size='1200x800', crop='top'):
        """
        Возвращает preview изображения указанного размера с обрезкой сверху.
        """
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def get_thumbnail_bottom(self, size='1200x800', crop='bottom'):
        """
        Возвращает preview изображения указанного размера с обрезкой снизу.
        """
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def thumbnail_center_detail_page(self, size='1500x800', crop='center'):
        """
        Возвращает preview изображения указанного размера с обрезкой по центру.
        """
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def thumbnail_right_detail_page(self, size='1500x800', crop='right'):
        """
        Возвращает preview изображения указанного размера с обрезкой справа.
        """
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def thumbnail_left_detail_page(self, size='1500x800', crop='left'):
        """
        Возвращает preview изображения указанного размера с обрезкой слева.
        """
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def thumbnail_top_detail_page(self, size='1500x800', crop='top'):
        """
        Возвращает preview изображения указанного размера с обрезкой сверху.
        """
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def thumbnail_bottom_detail_page(self, size='1500x800', crop='bottom'):
        """
        Возвращает preview изображения указанного размера с обрезкой по центру.
        """
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def small_thumbnail(self, size='700x400', crop='center'):
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

    @property
    def get_thumbnail_list(self, size='393x225', crop='center'):
        return get_thumbnail(self.image, size, crop=crop, quality=99).url

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
        verbose_name = 'Фото для слайдера'
        verbose_name_plural = 'Фото для слайдера'

    def __str__(self):
        return self.image_news.title

    @property
    def slider_thumbnail(self, size='1800x1200', crop=None):
        return get_thumbnail(self.slider_image, size, crop=crop, quality=99).url
