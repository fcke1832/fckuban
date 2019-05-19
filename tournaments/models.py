from sorl.thumbnail import ImageField, get_thumbnail
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

    def calculate_statistics(self):
        tours = self.get_tours()
        teams = self.get_teams()
        for team in teams:
            team.reset_statistic()
        for tour in tours:
            tour_matches = tour.matchtour_set.filter(is_active=True)
            for match in tour_matches:
                if match.home_team in teams and match.guest_team in teams:
                    match.calculate_resultes()

        for pos_number, team in enumerate(teams.order_by('-points', 'matches', '-win_matches', '-goals_difference', '-goals_scored', '-goals_scored_guest')):
            team.position_number = pos_number + 1
            team.save()

    def get_tours(self):
        return self.tours.filter(is_active=True)

    def get_teams(self):
        return self.team.filter(is_active=True)


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
    position_number = models.PositiveSmallIntegerField('Занимаемое место', blank=True, null=True)
    matches = models.PositiveSmallIntegerField('Матчи', default=0)
    win_matches = models.PositiveSmallIntegerField('Победы', default=0)
    draw_matches = models.PositiveSmallIntegerField('Ничьи', default=0)
    losing_matches = models.PositiveSmallIntegerField('Поражения', default=0)
    home_matches = models.PositiveSmallIntegerField('Сыграно домашних матчей', default=0)
    guest_matches = models.PositiveSmallIntegerField('Сыграно гостевых матчей', default=0)
    goals_scored = models.PositiveSmallIntegerField('Забито мячей', default=0)
    goals_scored_guest = models.PositiveSmallIntegerField('Забито мячей в гостях', default=0)
    goals_conceded = models.PositiveSmallIntegerField('Пропущено мячей', default=0)
    goals_difference = models.SmallIntegerField('Разница мячей', default=0)
    is_active = models.BooleanField('Активная', default=True)
    is_fcke = models.BooleanField('Наша команда', default=False)
    logo = ImageField('Логотип', default='', null=True, blank=True, upload_to='media/logo')

    def __str__(self):
        return '{}({})'.format(self.name, self.location)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'
        ordering = ('position_number', 'win_matches', 'win_matches', 'goals_scored', 'goals_scored_guest',)

    def reset_statistic(self):
        """
        Сброс статистики на дефолтное значение
        """
        self.points = \
        self.matches = \
        self.win_matches = \
        self.losing_matches = \
        self.draw_matches = \
        self.home_matches = \
        self.guest_matches = \
        self.goals_scored = \
        self.goals_scored_guest = \
        self.goals_conceded = \
        self.goals_difference = 0
        self.save()

    @property
    def get_thumbnail_logo(self, size='80x80', crop='center'):
        return get_thumbnail(self.logo, size, crop=crop, quality=99).url


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

    def calculate_resultes(self):
        """
        Подсчет и запись результата матча
        """
        self.home_team.matches += 1
        self.home_team.home_matches += 1
        self.home_team.goals_scored += self.home_goals
        self.home_team.goals_conceded += self.guest_goals
        self.home_team.goals_difference = self.home_team.goals_scored - self.home_team.goals_conceded

        self.guest_team.matches += 1
        self.guest_team.guest_matches += 1
        self.guest_team.goals_scored += self.guest_goals
        self.guest_team.goals_scored_guest += self.guest_goals
        self.guest_team.goals_conceded += self.home_goals
        self.guest_team.goals_difference = self.guest_team.goals_scored - self.guest_team.goals_conceded

        if self.home_goals > self.guest_goals:
            self.home_team.win_matches += 1
            self.home_team.points += 3
            self.guest_team.losing_matches += 1
        elif self.home_goals < self.guest_goals:
            self.guest_team.win_matches += 1
            self.guest_team.points += 3
            self.home_team.losing_matches += 1
        else:
            self.home_team.draw_matches += 1
            self.home_team.points += 1
            self.guest_team.draw_matches += 1
            self.guest_team.points += 1

        self.home_team.save()
        self.guest_team.save()
