from sorl.thumbnail import ImageField
from django.db import models


class BirthdayItem(models.Model):
    """
    Модель для именинников
    """
    CENTER, TOP, BOTTOM = range(3)
    CROP_CHOICES = (
        (CENTER, 'По центру'),
        (TOP, 'Сверху'),
        (BOTTOM, 'Снизу')
    )

    name = models.CharField("Имя", max_length=50)
    second_name = models.CharField("Фамилия", max_length=50, default="")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    image = ImageField('Фото', default='', null=True, blank=True, upload_to='media/birthdays_upload', help_text='Размер фото 92x92')
    crop_image = models.PositiveSmallIntegerField('Выравнивание фото', choices=CROP_CHOICES, default=CENTER)

    def __str__(self):
        return "{} {}".format(self.name, self.second_name)

    class Meta:
        verbose_name = 'Именинник'
        verbose_name_plural = 'Именинники'
