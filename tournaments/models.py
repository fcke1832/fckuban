from sorl.thumbnail import ImageField
from django.db import models
from django.core.validators import MaxValueValidator


class Tournament(models.Model):
    title = models.CharField('Название турнира', max_length=200)
    on_main = models.BooleanField('Текущий турнир', default=False)
    in_calendar = models.BooleanField('В календаре', default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'
        ordering = ('on_main', 'in_calendar',)


class Tour(models.Model):
    number = models.PositiveSmallIntegerField(
        '№ тура',
        validators=[MaxValueValidator(30)]
    )
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.SET_NULL,
        verbose_name='Турнир',
        related_name='tours',
        blank=True, null=True
    )
    is_active = models.BooleanField('Активный', default=True)

    def __str__(self):
        return "{}-й тур {}".format(str(self.number), self.tournament.title)

    class Meta:
        verbose_name = 'Тур'
        verbose_name_plural = 'Туры'
        ordering = ('number',)


class Team(models.Model):
    name = models.CharField('Команда', max_length=30)
    location = models.CharField('Населённый пункт', blank=True, null=True, max_length=50)
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.SET_NULL,
        verbose_name='Турнир',
        related_name='team',
        blank=True, null=True
    )
    points = models.PositiveSmallIntegerField('Очки', default=0)
    matches = models.PositiveSmallIntegerField('Матчи', default=0)
    win_matches = models.PositiveSmallIntegerField('Победы', default=0)
    losing_matches = models.PositiveSmallIntegerField('Поражения', default=0)
    draw_matches = models.PositiveSmallIntegerField('Ничьи', default=0)
    home_matches = models.PositiveSmallIntegerField('Сыграно домашних матчей', default=0)
    guest_matches = models.PositiveSmallIntegerField('Сыграно гостевых матчей', default=0)
    goals_scored = models.PositiveSmallIntegerField('Забито мячей', default=0)
    goals_scored_guest = models.PositiveSmallIntegerField('Забито мячей в гостях', default=0)
    goals_conceded = models.PositiveSmallIntegerField('Пропущено мячей', default=0)
    goals_difference = models.SmallIntegerField('Разница мячей', default=0)
    is_active = models.BooleanField('Активная', default=True)
    is_fcke = models.BooleanField('Наша команда', default=False)
    logo = ImageField('Логотип', default='', null=True, blank=True, upload_to='media/logo')
    position_number = models.PositiveSmallIntegerField('Занимаемое место', blank=True, null=True)

    def __str__(self):
        return '{}({})'.format(self.name, self.location)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'
        ordering = ('position_number', 'win_matches', 'win_matches', 'goals_scored', 'goals_scored_guest',)

    def get_tournament_statistics(self):
        pass


class MatchTour(models.Model):
    tour = models.ForeignKey(
        Tour, verbose_name='Тур',
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name='Хозяева',
        related_name='home_match_tour',
        null=False, blank=False
    )
    guest_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name='Гости',
        related_name='guest_match_tour',
        null=False, blank=False
    )
    is_active = models.BooleanField('Включить в таблицу', default=True)
    home_goals = models.PositiveSmallIntegerField('Голы хозяев', default=0)
    guest_goals = models.PositiveSmallIntegerField('Голы гостей', default=0)
    start_time = models.DateTimeField('Время начала матча', blank=True, null=True)
    is_finished = models.BooleanField('Матч прошёл', default=False)
    is_canceled = models.BooleanField('Матч отменён', default=False)

    def __str__(self):
        return '{}({}) - {}({})'.format(
            self.home_team.name, self.home_team.location,
            self.guest_team.name, self.guest_team.location,
        )

    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'
