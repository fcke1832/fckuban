from django.template.defaultfilters import date
from django.utils import timezone
from django.utils.translation import activate
from .models import BirthdayItem


def check_now():
    return timezone.now()


def current_month_birtdays():
    """
    Получаем именниников в текущем месяце
    """
    now = check_now()
    birthdays = BirthdayItem.objects.filter(date_of_birth__month=now.month)
    return birthdays


def current_month_name():
    """
    Название текущего месяца на русском
    """
    activate('ru')
    now = check_now()
    return date(now, 'F')
