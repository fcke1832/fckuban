# TESTING.md — запуск тестов

Тесты написаны на **pytest + pytest-django**. Пока проект живёт на
**Python 3.6 / Django 2.0.7**, используются версии, совместимые с этим стеком.

## Текущий стек (Python 3.6, Django 2.0.7)

```bash
python3.6 -m venv venv
venv/bin/pip install -r requirements-no-mysql.txt
venv/bin/pip install pytest==6.2.5 pytest-django==4.1.0 pytest-cov==3.0.0 coverage==6.2
```

Запуск:

```bash
venv/bin/python -m pytest
venv/bin/python -m pytest --cov --cov-report=term-missing
venv/bin/python -m pytest --cov --cov-report=html   # htmlcov/index.html
```

## Конфигурация

- `pytest.ini` — `DJANGO_SETTINGS_MODULE=fckuban.test_settings`,
  `python_files = tests.py test_*.py`, `testpaths` по приложениям.
- `fckuban/test_settings.py` — SQLite `:memory:`, временный `MEDIA_ROOT`,
  быстрый хешер паролей. Боевые настройки не переопределяются.
- `.coveragerc` — branch coverage, исключены миграции/тесты/`wsgi.py`/venv.
- `conftest.py` — общие фикстуры.

## Важно: `--nomigrations`

В `pytest.ini` включён `--nomigrations`, потому что миграция
`team/migrations/0007_auto_20190509_2142.py` импортирует живую модель и падает
на чистой БД (см. `BUGS.md`, BUG-023). После исправления миграции флаг можно
убрать и проверить создание БД с нуля:

```bash
venv/bin/python manage.py migrate
venv/bin/python -m pytest
```

## После перехода на Django 5.x / Python 3.14

Ограничивающие версии pytest/pytest-django/coverage больше не нужны:

```bash
uv add --dev pytest pytest-django pytest-cov
uv run pytest --cov
```

Тесты написаны так, чтобы не зависеть от деталей Django 2.0 (кроме
`news/admin.py:13` и `banner/admin.py:20` — см. `BUGS.md`).

## Найденные дефекты

Все ошибки, обнаруженные тестами, и закомментированные «правильные» проверки
описаны в [`BUGS.md`](BUGS.md). Код приложения намеренно не исправлялся.
