from django.db import models


class TicketProgram(models.Model):
    """
    Модель билетной программы
    """
    name = models.CharField('Название билетной программы', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Билетная программа'
        verbose_name_plural = 'Билетные программы'


class Tribune(models.Model):
    """
    Модель трибуны, которая входит в билетную программу и включает в себя сектора
    """
    name = models.CharField('Наименование трибуны', max_length=50)
    is_sale = models.BooleanField('В продаже', default=False)
    ticket_program = models.ForeignKey(TicketProgram, models.CASCADE, related_name='tribunes')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Трибуна'
        verbose_name_plural = 'Трибуны'


class Sector(models.Model):
    """
    Модель сектора, которая в себя включает наименование сектора и цену
    """
    name = models.CharField('Наименование сектора', max_length=30)
    price = models.CharField('Цена', max_length=5)
    tribune = models.ForeignKey(Tribune, models.CASCADE, verbose_name='Трибуна')
    is_sale = models.BooleanField('В продаже', default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сектор'
        verbose_name_plural = 'Сектора'


class TicketSaleWidget(models.Model):
    """
    Модель для вставки виджета онлайн продажи билетов стороннего сервиса
    """
    link = models.URLField('Ссылка стороннего сервиса')
    is_active = models.BooleanField('Онлайн-продажа открыта', default=True)

    class Meta:
        verbose_name = 'Ссылка на виджет онлайн-продажи билетов'
        verbose_name_plural = 'Ссылки на виджет онлайн-продажи билетов'
