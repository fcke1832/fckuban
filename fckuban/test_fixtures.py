"""Смоук-тест демонстрационных фикстур из ``fixtures/``.

Проверяет, что набор фикстур загружается на текущей версии Django и что
количество объектов соответствует документации (``fixtures/README.md``).
"""

import pytest
from django.apps import apps
from django.core.management import call_command

FIXTURES = [
    "fixtures/tournaments.json",
    "fixtures/team.json",
    "fixtures/partners.json",
    "fixtures/news.json",
    "fixtures/medialinks.json",
    "fixtures/calendar_matches.json",
    "fixtures/birthdays.json",
    "fixtures/banner.json",
]

EXPECTED_COUNTS = {
    ("tournaments", "Tournament"): 3,
    ("tournaments", "Tour"): 6,
    ("tournaments", "Team"): 8,
    ("tournaments", "MatchTour"): 16,
    ("team", "Player"): 10,
    ("team", "Coach"): 3,
    ("partners", "Partner"): 4,
    ("news", "News"): 4,
    ("news", "NewsHashTag"): 5,
    ("news", "NewsImage"): 4,
    ("medialinks", "Article"): 2,
    ("calendar_matches", "Match"): 6,
    ("birthdays", "BirthdayItem"): 5,
    ("banner", "Banner"): 2,
}


@pytest.mark.django_db
def test_demo_fixtures_load() -> None:
    """Фикстуры загружаются, объекты создаются в ожидаемом количестве."""
    call_command("loaddata", *FIXTURES, verbosity=0)

    for (app_label, model_name), expected in EXPECTED_COUNTS.items():
        model = apps.get_model(app_label, model_name)
        assert model.objects.count() == expected, f"{app_label}.{model_name}"


@pytest.mark.django_db
def test_demo_fixtures_load_twice_idempotent() -> None:
    """Повторный loaddata обновляет записи по pk и не создаёт дубликаты."""
    call_command("loaddata", *FIXTURES, verbosity=0)
    call_command("loaddata", *FIXTURES, verbosity=0)

    for (app_label, model_name), expected in EXPECTED_COUNTS.items():
        model = apps.get_model(app_label, model_name)
        assert model.objects.count() == expected, f"{app_label}.{model_name}"
