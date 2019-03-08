import calendar
import locale
from fckuban.utils import check_now
from .models import BirthdayItem


def today_birtdays():
    """
    Получаем именниников в текущем дне
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
