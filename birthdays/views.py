from django.utils import timezone
from .models import BirthdayItem


def current_month_birtdays():
    """
    Получаем именниников в текущем месяце
    """
    now = timezone.now()
    birthdays = BirthdayItem.objects.all()
    return birthdays
