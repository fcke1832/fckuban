from django.db import models
from sorl.thumbnail import ImageField


class Banner(models.Model):
    title = models.CharField('Заголовок', max_length=100)
    published = models.BooleanField('Опубликовать', default=False)
    image = ImageField('Баннер на главной', default='', null=None, blank=False, upload_to='media/banners', help_text="Оптимальный размер баннера 960x790")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'
