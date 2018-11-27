from django.db import models


class BirthdayItem(models.Model):
    """
    Модель для именинников
    """
    name = models.CharField("Имя и фамилия", max_length=200)
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Дата рождения")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Именинник'
        verbose_name_plural = 'Именинники'