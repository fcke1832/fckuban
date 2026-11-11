"""Тесты приложения birthdays."""

import datetime
import locale

import pytest
from django.contrib import admin
from django.test import RequestFactory
from django.utils import timezone

from birthdays.admin import BirthdayItemAdmin
from birthdays.apps import BirthdaysConfig
from birthdays.models import BirthdayItem
from birthdays.views import check_today, today_birtdays


@pytest.fixture
def require_ru_locale(ru_locale_available):
    """Пропускает тест, если в системе нет локали ru_RU.UTF-8."""
    if not ru_locale_available:
        pytest.skip("locale ru_RU.UTF-8 is not installed")


class TestBirthdaysConfig:
    def test_app_config(self):
        assert BirthdaysConfig.name == "birthdays"


@pytest.mark.django_db
class TestBirthdayItemModel:
    def test_str(self):
        item = BirthdayItem(name="Иван", second_name="Иванов")
        assert str(item) == "Иван Иванов"

    def test_str_with_empty_second_name(self):
        item = BirthdayItem(name="Иван")
        assert str(item) == "Иван "

    def test_defaults(self):
        item = BirthdayItem.objects.create(name="Иван")
        assert item.second_name == ""
        assert item.date_of_birth is None
        assert item.image.name == ""
        assert item.crop_image == BirthdayItem.CENTER

    def test_crop_choices(self):
        assert dict(BirthdayItem.CROP_CHOICES) == {
            0: "По центру",
            1: "Сверху",
            2: "Снизу",
        }

    def test_meta(self):
        assert BirthdayItem._meta.verbose_name == "Именинник"
        assert BirthdayItem._meta.verbose_name_plural == "Именинники"
        assert BirthdayItem._meta.get_field("image").upload_to == "media/birthdays_upload"


@pytest.mark.django_db
class TestBirthdayViews:
    def test_today_birtdays_returns_only_today(self, monkeypatch):
        fixed_now = timezone.make_aware(datetime.datetime(2024, 11, 3, 12, 0))
        monkeypatch.setattr("birthdays.views.check_now", lambda: fixed_now)

        today_one = BirthdayItem.objects.create(
            name="Сегодня",
            date_of_birth=datetime.date(1990, 11, 3),
        )
        today_two = BirthdayItem.objects.create(
            name="Тоже сегодня",
            date_of_birth=datetime.date(2000, 11, 3),
        )
        BirthdayItem.objects.create(name="Завтра", date_of_birth=datetime.date(1990, 11, 4))
        BirthdayItem.objects.create(name="Без даты", date_of_birth=None)

        result = list(today_birtdays())

        assert result == [today_one, today_two]

    def test_today_birtdays_empty(self, monkeypatch):
        fixed_now = timezone.make_aware(datetime.datetime(2024, 1, 1, 12, 0))
        monkeypatch.setattr("birthdays.views.check_now", lambda: fixed_now)

        BirthdayItem.objects.create(name="Летний", date_of_birth=datetime.date(1990, 7, 1))

        assert list(today_birtdays()) == []

    def test_check_today_formats_russian_date(self, monkeypatch, require_ru_locale):
        fixed_now = timezone.make_aware(datetime.datetime(2024, 11, 3, 12, 0))
        monkeypatch.setattr("birthdays.views.check_now", lambda: fixed_now)

        result = check_today()

        assert result.endswith("ноября")
        assert result.startswith("3 ")

    def test_check_today_uses_current_day_number(self, monkeypatch):
        fixed_now = timezone.make_aware(datetime.datetime(2024, 1, 9, 23, 59))
        monkeypatch.setattr("birthdays.views.check_now", lambda: fixed_now)

        assert check_today().startswith("9 ")

    def test_check_today_requires_system_locale(self, monkeypatch):
        """БАГ-024: локаль ru_RU.UTF-8 захардкожена и может отсутствовать в системе."""

        def broken_setlocale(*args, **kwargs):
            raise locale.Error("locale not installed")

        monkeypatch.setattr("birthdays.views.locale.setlocale", broken_setlocale)

        # Ожидаемое поведение: функция не должна зависеть от системной локали.
        # assert check_today()
        with pytest.raises(locale.Error):
            check_today()


@pytest.mark.django_db
class TestBirthdayItemAdmin:
    def test_registered_and_config(self):
        model_admin = BirthdayItemAdmin(BirthdayItem, admin.site)
        assert model_admin.list_display == ("name", "second_name", "date_of_birth")
        assert model_admin.date_hierarchy == "date_of_birth"
        assert model_admin.actions == ["download_csv"]
        assert BirthdayItem in admin.site._registry

    def test_download_csv_uses_selected_month(self):
        BirthdayItem.objects.create(
            name="Ноябрьский",
            second_name="Иванов",
            date_of_birth=datetime.date(1990, 11, 3),
        )
        BirthdayItem.objects.create(
            name="Июльский",
            second_name="Петров",
            date_of_birth=datetime.date(1990, 7, 3),
        )
        model_admin = BirthdayItemAdmin(BirthdayItem, admin.site)
        request = RequestFactory().get("/admin/birthdays/birthdayitem/")
        queryset = BirthdayItem.objects.filter(name="Ноябрьский")

        response = model_admin.download_csv(request, queryset)

        content = (
            b"".join(response.streaming_content).decode("utf-8")
            if response.streaming
            else response.content.decode("utf-8")
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        assert "somefilename.csv" in response["Content-Disposition"]
        assert "Ноябрьский" in content
        assert "Июльский" not in content

    def test_download_csv_empty_queryset_falls_back_to_january(self):
        BirthdayItem.objects.create(
            name="Январский",
            second_name="Сидоров",
            date_of_birth=datetime.date(1990, 1, 3),
        )
        model_admin = BirthdayItemAdmin(BirthdayItem, admin.site)
        request = RequestFactory().get("/admin/birthdays/birthdayitem/")

        response = model_admin.download_csv(request, BirthdayItem.objects.none())

        content = response.content.decode("utf-8")
        assert "Январский" in content

    def test_download_csv_short_description(self):
        assert BirthdayItemAdmin.download_csv.short_description == ("Скачать список именинников за выбранный месяц")
