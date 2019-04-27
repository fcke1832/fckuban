from sorl.thumbnail import ImageField
from transliterate import translit
from django.db import models
from django.utils.text import slugify


class BaseTeamMember(models.Model):
    full_name = models.CharField('ФИО', max_length=200)
    birthday = models.DateField('Дата рождения')
    image = ImageField(
        'Фото',
        default='',
        null=True,
        blank=True,
        upload_to='media/team_upload',
        help_text='Размер фото 150x250'
    )
    slug = models.SlugField('ЧПУ', max_length=200, null=True, blank=True, unique=True)

    def get_second_name(self):
        return self.full_name.split()[0]

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(translit(str(self.full_name), 'ru', reversed=True))
            self.slug = slug
        super(BaseTeamMember, self).save(*args, **kwargs)


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
