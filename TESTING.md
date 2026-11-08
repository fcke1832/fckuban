# TESTING.md — тесты и локальная проверка

Стек: **Python 3.14 + Django 5.2 LTS**, зависимости и запуск — через **uv**
(см. `pyproject.toml` / `uv.lock`).

## Установка окружения

```bash
uv sync            # создаёт .venv на Python 3.14 и ставит зависимости
```

## Запуск тестов

```bash
uv run pytest
uv run pytest --cov --cov-report=term-missing
uv run pytest --cov --cov-report=html   # htmlcov/index.html
```

Текущий результат: **301 passed**, покрытие — 99 %+ (см. отчёт
`UPGRADE_PY314_DJ52.md`).

## Конфигурация

- `pytest.ini` — `DJANGO_SETTINGS_MODULE=fckuban.test_settings`,
  `python_files = tests.py test_*.py *_tests.py`, `testpaths` по приложениям.
- `fckuban/test_settings.py` — SQLite `:memory:`, временный `MEDIA_ROOT`,
  быстрый хешер паролей. Боевые настройки не переопределяются.
- `.coveragerc` — branch coverage, исключены миграции/тесты/`wsgi.py`/venv.
- `conftest.py` — общие фикстуры (изображение, пользователи, локаль).
- `fckuban/test_fixtures.py` — смоук-тест: демонстрационные фикстуры из
  `fixtures/` загружаются и повторный `loaddata` не создаёт дубликаты.

## `pytest`, а не `manage.py test`

Тесты написаны в pytest-стиле (функции и обычные классы `Test*`, а не
`unittest.TestCase`), поэтому стандартный раннер Django их не видит:

```bash
uv run python manage.py test   # Ran 0 tests
```

Единственная правильная команда — `uv run pytest`. В `AGENTS.md` указана
команда `python manage.py pytest` — такой команды в Django нет, это
расхождение документации с кодом.

## Миграции

`--nomigrations` больше не используется: BUG-023 исправлен, тестовая БД
строится реальными миграциями. Проверка чистой БД:

```bash
uv run python manage.py migrate
uv run pytest
```

## Локальный запуск и фикстуры

```bash
uv run python manage.py migrate          # SQLite: db.sqlite3
./fixtures/load_fixtures.sh              # демо-данные + картинки
uv run python manage.py createsuperuser  # для входа в /admin/
uv run python manage.py runserver
```

`DEBUG = True` для разработки задаётся в `fckuban/local_settings.py`
(не попадает в git). Подробности по фикстурам — `fixtures/README.md`.

## Найденные дефекты

Все ошибки, обнаруженные тестами, и закомментированные «правильные» проверки
описаны в [`BUGS.md`](BUGS.md).
