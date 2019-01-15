from django.utils import timezone
from .models import BirthdayItem


def current_month_birtdays():
    """
    Получаем именниников в текущем месяце
    """
    now = timezone.now()
    birthdays = BirthdayItem.objects.filter(date_of_birth__month=now.month)
    return birthdays
