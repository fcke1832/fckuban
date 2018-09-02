from django.db import models


class YoutubeLink(models.Model):
    link = models.URLField('Ссылка на Youtube', help_text='Ссылка должна начинаться с \"https://www.youtube.com/embed/...\"')
    description = models.CharField('Описание ролика', max_length=200)

    def __str__(self):
        return self.description


class SocialNetworkLink(models.Model):
    name = models.CharField('Название', max_length=30)
    link = models.URLField('Ссылка')

    def __str__(self):
        return self.name