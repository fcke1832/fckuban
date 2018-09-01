from django.db import models


class Tournament(models.Model):
    title = models.CharField('Название турнира', max_length=200)
    on_main = models.BooleanField('На главной', default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'


class Team(models.Model):
    name = models.CharField('Команда', max_length=50)
    tournament = models.ForeignKey(Tournament, models.SET_NULL, verbose_name='Турнир', related_name='team', blank=True, null=True)
    points = models.PositiveSmallIntegerField('Очки', default=0)
    matches = models.PositiveSmallIntegerField('Матчи', default=0)
    is_active = models.BooleanField('Активная', default=True)
    is_fcke = models.BooleanField('Наша команда', default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'