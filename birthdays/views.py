import calendar
import locale
from django.utils import timezone
from .models import BirthdayItem


def check_now():
    return timezone.now()


def today_birtdays():
    """
    Получаем именниников в текущем месяце
    """
    now = check_now()
    birthdays = BirthdayItem.objects.filter(date_of_birth__month=now.month, date_of_birth__day=now.day)
    return birthdays


def check_today():
    """
    Название текущего месяца и даты на русском
    """
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    now = check_now()
    day = now.day
    month = calendar.month_name[now.month.numerator]
    return "{} {}".format(day, month)
