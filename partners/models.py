from sorl.thumbnail import ImageField, get_thumbnail
from django.db import models


class Partner(models.Model):
    PARTNER, SPONSOR = 1, 2
    PARTNER_CHOICES = (
        (PARTNER, 'Партнёр'),
        (SPONSOR, 'Спонсор'),
    )
    title = models.CharField('Название', max_length=100)
    link = models.URLField('Ссылка на сайт', blank=True, null=True)
    contacts = models.CharField('Контакты', max_length=50, blank=True, null=True)
    description = models.CharField('Описание', blank=True, null=True, max_length=255)
    image = ImageField(
        'Загрузить логотип',
        default='',
        null=True,
        blank=True,
        upload_to='media/partners_upload',
        help_text='Размер фото 70x70'
    )
    type_partner = models.PositiveSmallIntegerField('Тип партнёрства', choices=PARTNER_CHOICES, default=PARTNER)
    is_active = models.BooleanField('Активный', default=False)
    number = models.PositiveSmallIntegerField('Порядковый номер', default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Партнёр'
        verbose_name_plural = 'Партнёры'
        ordering = ('-number', 'title',)

    @property
    def logo_thumbnail(self, size='70x70'):
        return get_thumbnail(self.image, size, quality=99).url
