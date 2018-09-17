from django.db import models
from embed_video.fields import EmbedVideoField


class YoutubeLink(models.Model):
    link = EmbedVideoField('Ссылка на Youtube')
    description = models.CharField('Описание ролика', max_length=200)
    on_main = models.BooleanField('На главной', default=False)
    date_pub = models.DateTimeField('Дата публикации', auto_now=True)

    def __str__(self):
        return self.description


class SocialNetworkLink(models.Model):
    name = models.CharField('Название', max_length=30)
    link = models.URLField('Ссылка')

    def __str__(self):
        return self.name


class MapsLink(models.Model):
    name = models.CharField('Название', max_length=30)
    link = models.URLField('Ссылка  ')

    def __str__(self):
        return self.name