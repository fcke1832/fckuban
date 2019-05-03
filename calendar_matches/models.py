from django.db import models
from tournaments.models import Team, Tournament
from tickets.models import TicketProgram


class Match(models.Model):
    is_active = models.BooleanField('В календаре на главной', default=False)
    home_team = models.ForeignKey(Team, models.CASCADE, verbose_name='Хозяева', related_name='home_match')
    guest_team = models.ForeignKey(Team, models.CASCADE, verbose_name='Гости', related_name='guest_match')
    tournament = models.ForeignKey(Tournament, models.CASCADE, verbose_name='Турнир', related_name='match')
    stadium = models.CharField('Место проведения', max_length=200, blank=True, null=True)
    start_time = models.DateTimeField('Время начала матча', blank=True, null=True)
    is_finished = models.BooleanField('Матч прошёл', default=False)
    is_canceled = models.BooleanField('Матч отменён', default=False)
    home_goals = models.PositiveSmallIntegerField('Голы хозяев', default=0)
    guest_goals = models.PositiveSmallIntegerField('Голы гостей', default=0)
    tour = models.CharField('Тур', max_length=10, blank=True, null=True)
    time_invisible = models.BooleanField('Скрыть время', default=False)
    ticket_program = models.ForeignKey(
        TicketProgram,
        verbose_name='Билетная программа',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    link_tickets = models.URLField('Ссылка на онлайн-продажу билетов', blank=True, null=True)

    def __str__(self):
        return '{0} - {1}'.format(self.home_team, self.guest_team)

    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'
        ordering = ['-start_time', '-is_finished']
