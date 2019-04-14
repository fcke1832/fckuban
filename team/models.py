from sorl.thumbnail import ImageField
from django.db import models


class BaseTeamMember(models.Model):
    full_name = models.CharField('ФИО', max_length=200)
    birthday = models.DateField('Дата рождения')
    image = ImageField(
        'Фото',
        default='',
        null=None,
        blank=False,
        upload_to='media/team_upload',
        help_text='Размер фото 150x250'
    )


class Player(BaseTeamMember):
    GOALKEEPER, DEFENDER, MIDFIELDER, FORWARD = range(4)
    POSITION_CHOICES = (
        (GOALKEEPER, 'Вратарь'),
        (DEFENDER, 'Защитник'),
        (MIDFIELDER, 'Полузащитник'),
        (FORWARD, 'Нападающий'),
    )

    position = models.PositiveSmallIntegerField('Амплуа', choices=POSITION_CHOICES, default=GOALKEEPER)
    weight = models.PositiveSmallIntegerField('Вес(кг)', default=0)
    growth = models.PositiveSmallIntegerField('Рост(см)', default=0)
    number = models.PositiveSmallIntegerField('Номер', default=0)

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"

    def __str__(self):
        return self.full_name


class Coach(BaseTeamMember):
    MANAGER, ASSISTANT_COACH, GOALKEEPER_COACH = range(3)
    POSITION_CHOICES = (
        (MANAGER, 'Главный тренер'),
        (ASSISTANT_COACH, 'Старший тренер'),
        (GOALKEEPER_COACH, 'Тренер вратарей'),
    )

    position = models.PositiveSmallIntegerField('Должность', choices=POSITION_CHOICES, default=ASSISTANT_COACH)

    class Meta:
        verbose_name = "Тренер"
        verbose_name_plural = "Тренерский штаб"

    def __str__(self):
        return self.full_name
