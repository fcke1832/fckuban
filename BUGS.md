# BUGS.md — ошибки, найденные при покрытии проекта тестами

Дата: 2026-11-03
Стек на момент проверки: **Python 3.6.15, Django 2.0.7, SQLite**.
Тестовый набор: **299 тестов, покрытие 99.24 % (branch coverage), 99.8 % строк**.
Код приложения при этом **намеренно не исправлялся**: тесты фиксируют текущее
поведение, а ожидаемые (правильные) проверки закомментированы с пометкой `БАГ-NNN`.

Запуск тестов и отчёта о покрытии:

```bash
venv/bin/python -m pytest
venv/bin/python -m pytest --cov --cov-report=term-missing
```

> **Важно для перехода на Django 5.x.** Многие ошибки ниже в Django 2.0.7
> «молча» проглатываются шаблонизатором. Начиная с Django 2.1 такие исключения
> в `{% include %}` больше не подавляются, а в Django 5.x они гарантированно
> приводят к 500. Поэтому эти пункты — не косметика, а реальные блокеры
> обновления.

## Сводная таблица

| ID | Важность | Компонент | Кратко | Тест |
|----|----------|-----------|--------|------|
| BUG-001 | Критично | `fckuban`, `medialinks`, `news`, `partners`, `tournaments` | `IndexError` на страницах при пустом календаре матчей | `test_*_fails_without_calendar_matches` |
| BUG-002 | Низкая | `tournaments.Team` | `__str__` выводит `None` вместо пустого города | `TestTeam::test_str_without_location` |
| BUG-003 | Средняя | `*/apps.py`, `settings.INSTALLED_APPS` | Кастомные `AppConfig` не применяются в Django 2.0 | `TestTranslationApp::test_app_config` |
| BUG-004 | Высокая | `partners` | Падение списка партнёров без логотипа | `test_page_fails_when_partner_has_no_logo` |
| BUG-005 | Низкая | `team` | Тренерский штаб не выводится на странице команды | `test_coaches_are_not_rendered_in_template` |
| BUG-006 | Средняя | `team` | Неуникальный `slug` ломает страницу игрока/тренера | `test_duplicate_slug_breaks_detail_page` |
| BUG-007 | Средняя | `team` | Шаблон `coach.html` пустой | `test_coach_template_is_empty` |
| BUG-008 | Средняя | `team` | `BaseTeamMember` не `abstract` — лишняя таблица | `TestPlayer::test_meta` |
| BUG-009 | Высокая | `team` | Страница игрока падает без фото | `test_player_detail_fails_without_image` |
| BUG-010 | Средняя | `news`, `medialinks` | Черновики доступны по прямому URL | `test_unpublished_*_is_accessible` |
| BUG-011 | Высокая | `medialinks` | Превью статьи падает без изображения | `test_get_thumbnail_fails_without_image` |
| BUG-012 | Низкая | `news` | Слаг новости содержит точку и не проходит `validate_slug` | `test_generated_slug_contains_dot` |
| BUG-013 | Низкая | `news` | Предпросмотр доступен любому авторизованному пользователю | `test_regular_authenticated_user_can_open_preview` |
| BUG-014 | Критично | `news` | Новость без фото роняет главную/детальную (500 после Django 2.1) | `test_detail_fails_without_image` |
| BUG-015 | Высокая | `tournaments` | В таблицу попадают отменённые и будущие матчи | `test_calculate_statistics_counts_canceled_and_future_matches` |
| BUG-016 | Низкая | `tournaments.Tour` | `__str__` падает, если турнир не задан | `test_str_without_tournament_fails` |
| BUG-017 | Высокая | `tournaments.MatchTour` | `calculate_resultes` считает отменённый матч | `test_calculate_resultes_counts_canceled_match` |
| BUG-018 | Средняя | `tournaments.admin` | Форма добавления тура падает при `resolver_match=None` | `test_formfield_for_foreignkey_without_resolver_match` |
| BUG-019 | Высокая | `fckuban.get_calendar_matches` | `start_time=None` роняет главную | `test_match_without_start_time_fails` |
| BUG-020 | Средняя | `fckuban.templatetags.calendar` | Не импортирован `Match` — тег календаря падает | `test_calendar_tournaments_tag`, `test_module_get_calendar_fails` |
| BUG-021 | Высокая | `fckuban.utils.image_path` | `md5(str)` — `TypeError` на Python 3 | `test_image_path_fails_with_str_digest` |
| BUG-022 | Низкая | `fckuban.templatetags.calendar` | Тег выводит строку `None` вместо пустоты | `test_current_tournament_tag_without_tournament` |
| BUG-023 | Критично | `team/migrations/0007` | Миграция импортирует живую модель, свежая БД не создаётся | `manage.py test` / `migrate` |
| BUG-024 | Средняя | `birthdays.views.check_today` | Захардкожена локаль `ru_RU.UTF-8` | `test_check_today_requires_system_locale` |

---

## BUG-001. `IndexError` на страницах при пустом календаре

**Где:**
- `fckuban/views.py:151`
- `medialinks/views.py:28` и `medialinks/views.py:60`
- `news/views.py:71`
- `partners/views.py:26`
- `tournaments/views.py:37`

**Причина.** В `try/except IndexError` при отсутствии будущих матчей код
подставляет `context['calendar_matches'][-1]`, но список `calendar_matches`
тоже пуст:

```python
except IndexError:
    context['future_match'] = context['calendar_matches'][-1]
```

**Как воспроизвести.** Не создавать ни одного `Match` с `is_active=True`
(или ни одного турнира с `in_calendar=True`) и открыть `/`, `/media/article_list/`,
`/partners/`, `/tournaments/standings/` или детальную новость/статью.

**Факт.** `IndexError: list index out of range`, HTTP 500.
**Ожидаемо.** `future_match = None` (или отсутствие ключа) и HTTP 200.

**Тесты.** `test_*_fails_without_calendar_matches` в `fckuban/tests.py`,
`medialinks/tests.py`, `news/tests.py`, `partners/tests.py`,
`tournaments/tests.py`. Ожидаемые проверки закомментированы.

**Риск для Django 5.x.** Ошибка возникает во view, а не в шаблоне, поэтому
проявится сразу и на 2.0, и на 5.x.

---

## BUG-002. `Team.__str__` выводит `None`

**Где:** `tournaments/models.py:90-91`.

`location` объявлен как `blank=True, null=True`, но:

```python
def __str__(self):
    return '{}({})'.format(self.name, self.location)
```

**Факт.** `"Кубань(None)"`; в админке и шаблонах это видно пользователю.
**Ожидаемо.** `"Кубань"` или `"Кубань()"` без `None`.

**Тест:** `tournaments/tests.py::TestTeam::test_str_without_location`.

---

## BUG-003. Кастомные `AppConfig` не применяются

**Где:** `fckuban/settings.py:48-59` (плоские имена приложений) и
`*/apps.py` (`BannerConfig`, `NewsConfig`, `TeamConfig`, `TournamentsConfig`,
`MedialinksConfig`, `PartnersConfig`, `LinksConfig`, `TranslationConfig`).

В `INSTALLED_APPS` указаны `'banner'`, `'news'`, `'team'` и т. д. В Django 2.0
этого недостаточно: нужен `default_app_config` в `__init__.py` или запись
`'banner.apps.BannerConfig'`. В результате `verbose_name` из конфигов
игнорируется, и в админке отображаются `Banner`, `News`, `Team` вместо
русских названий.

**Факт.** `apps.get_app_config('news').__class__ is AppConfig` → `True`.
**Ожидаемо.** Используется `NewsConfig` с `verbose_name = 'Новости'`.
**Примечание.** В Django 3.2+ конфиг находится автоматически, поэтому после
обновления поведение изменится; сейчас это расхождение кода и ожиданий.

**Тест:** `translation/tests.py::TestTranslationApp::test_app_config`
(ожидаемая проверка закомментирована).

---

## BUG-004. Падение списка партнёров без логотипа

**Где:** `partners/models.py:36-37`, шаблон `partners/templates/partners_list.html`.

```python
@property
def logo_thumbnail(self, size='70x70'):
    return get_thumbnail(self.image, size, quality=99).url
```

`image` необязателен (`null=True, blank=True`), но `get_thumbnail` для пустого
поля возвращает `None`, после чего `.url` даёт `AttributeError`.

**Факт.** HTTP 500 на `/partners/`, если есть активный партнёр без логотипа.
**Ожидаемо.** Заглушка/пустой `img` и HTTP 200.

**Тест:** `partners/tests.py::TestPartnerListView::test_page_fails_when_partner_has_no_logo`.

---

## BUG-005. Тренерский штаб не выводится на странице команды

**Где:** `team/views.py` передаёт `context['coaches']`, но
`team/templates/all_team.html` не содержит блока для `coaches`.

**Факт.** Тренеры есть в контексте, но не в HTML.
**Ожидаемо.** Тренеры отображаются на `/team/all_team/`.

**Тест:** `team/tests.py::TestTeamView::test_coaches_are_not_rendered_in_template`.

---

## BUG-006. Неуникальный `slug` ломает DetailView

**Где:** `team/models.py:39` — `slug = models.SlugField(..., null=True, blank=True)`
без `unique=True`; `team/urls.py` ищет объект по `slug`.

Два игрока/тренера с одинаковым ФИО получают одинаковый `slug`, и
`DetailView` выбрасывает `MultipleObjectsReturned`.

**Факт.** HTTP 500 на `/team/all_team/player/<slug>/`.
**Ожидаемо.** Уникальный `slug` (или разрешение коллизий при сохранении).

**Тест:** `team/tests.py::TestPlayerDetailView::test_duplicate_slug_breaks_detail_page`.

---

## BUG-007. Пустой шаблон `coach.html`

**Где:** `team/templates/coach.html` — файл нулевого размера.

**Факт.** Страница тренера отдаёт пустой HTML (HTTP 200).
**Ожидаемо.** Страница использует `base.html` и показывает тренера.

**Тест:** `team/tests.py::TestCoachDetailView::test_coach_template_is_empty`.

---

## BUG-008. `BaseTeamMember` не является абстрактной моделью

**Где:** `team/models.py:7` — `class BaseTeamMember(models.Model)` без
`class Meta: abstract = True`.

**Факт.** Создаётся отдельная таблица `team_baseteammember`; базовая модель
попадает в миграции и может отображаться в админке.
**Ожидаемо.** `BaseTeamMember._meta.abstract is True`, отдельной таблицы нет.

**Тест:** `team/tests.py::TestPlayer::test_meta`.

**Риск для обновления.** Исправление потребует отдельной миграции; трогать
её вручную в рамках текущей задачи нельзя.

---

## BUG-009. Страница игрока падает без фото

**Где:** `team/templates/player.html:10` — `{{ player.image.url }}` без проверки.

`image` необязателен (`null=True, blank=True`). Если файла нет, обращение к
`.url` выбрасывает `ValueError`.

**Факт.** HTTP 500 на странице игрока без фото.
**Ожидаемо.** Заглушка, как в `all_team.html` (`{% if keeper.image %}`).

**Тест:** `team/tests.py::TestPlayerDetailView::test_player_detail_fails_without_image`.

---

## BUG-010. Черновики доступны по прямому URL

**Где:** `news/views.py:74-80` (`NewsDetailView`), `medialinks/views.py:45-48`
(`ArticleDetailView`). `get_queryset` не переопределён, поэтому `DetailView`
отдаёт любую запись, включая `published=False`.

**Факт.** Через `/news/news_detail/<slug>/` и `/media/article_detail/<slug>/`
открывается неопубликованная новость/статья.
**Ожидаемо.** 404 для `published=False` (либо явная проверка прав).

**Тесты:**
- `news/tests.py::TestNewsDetailView::test_unpublished_news_is_accessible`
- `medialinks/tests.py::TestArticleDetailView::test_unpublished_article_is_accessible`

---

## BUG-011. Превью статьи падает без изображения

**Где:** `medialinks/models.py:59-64` — `get_thumbnail`/`get_thumbnail_list`
вызываются без проверки `self.image`.

**Факт.** `AttributeError: 'NoneType' object has no attribute 'url'`; список
СМИ падает, если у статьи нет картинки.
**Ожидаемо.** Пустой URL/заглушка.

**Тест:** `medialinks/tests.py::TestArticleModel::test_get_thumbnail_fails_without_image`.

---

## BUG-012. Слаг новости содержит точку

**Где:** `news/models.py:160-164`.

```python
slug += "-{}".format(datetime.now().timestamp())
```

`timestamp()` содержит `.`, а `SlugField`/`validate_slug` допускают только
буквы, цифры, `_` и `-`. Слаг сохраняется в БД без валидации, но не проходит
`full_clean()`/`validate_slug()` и выглядит невалидным для SEO/URL.

**Факт.** `validate_slug(news.slug)` → `ValidationError`.
**Ожидаемо.** Слаг без точки (например, timestamp без дробной части).

**Тест:** `news/tests.py::TestNewsModel::test_generated_slug_contains_dot`.

---

## BUG-013. Предпросмотр новостей доступен любому авторизованному

**Где:** `news/views.py:37-40`.

```python
if not user.is_authenticated and not user.is_superuser and not user.is_staff:
    return redirect(reverse('index'))
```

Из-за `and` условие срабатывает только для анонима. Любой залогиненный
пользователь получает HTTP 200, хотя шаблон `news_list_preview.html` показывает
контент только staff/superuser — пользователь видит пустую страницу.

**Ожидаемо.** Для обычного авторизованного пользователя — redirect (или 403).

**Тест:** `news/tests.py::TestNewsPreview::test_regular_authenticated_user_can_open_preview`.

---

## BUG-014. Новость без фото роняет главную и детальную страницу

**Где:** `news/models.py:78-147` (все `get_thumbnail*`), шаблоны
`fckuban/templates/mainpage/news.html`, `news/templates/news_detail.html`,
`news/templates/news_list.html`.

`News.image` имеет `default=''`, а свойства вызывают `get_thumbnail(...).url`
без проверки. Для записи без файла `get_thumbnail` возвращает `None` →
`AttributeError`.

**Факт.** В Django 2.0.7 исключение внутри `{% include %}` подавляется
(`RemovedInDjango21Warning`), и главная просто теряет блок новостей.
В Django 2.1+ это уже ошибка, в Django 5.x — HTTP 500.
**Ожидаемо.** Проверка наличия изображения и заглушка.

**Тест:** `news/tests.py::TestNewsDetailView::test_detail_fails_without_image`.
Дополнительно предупреждение воспроизводилось на главной (тест
`test_main_page_publishes_periodic_news` до патча превью).

**Это главный блокер обновления:** после перехода на Django 5.x любая новость
без файла положит главную страницу.

---

## BUG-015. В таблицу попадают отменённые и будущие матчи

**Где:** `tournaments/models.py:19-28`.

```python
tour_matches = tour.matchtour_set.filter(is_active=True)
...
match.calculate_resultes()
```

Нет фильтра по `is_finished=True` и `is_canceled=False`. Будущий матч со
счётом по умолчанию `0:0` считается ничьей, отменённый — победой/поражением.

**Факт.** После пересчёта у команды появляются матчи и очки за ещё не
сыгранные/отменённые игры.
**Ожидаемо.** Учитывать только `is_active=True, is_finished=True, is_canceled=False`.

**Тест:** `tournaments/tests.py::TestTournament::test_calculate_statistics_counts_canceled_and_future_matches`.

---

## BUG-016. `Tour.__str__` падает без турнира

**Где:** `tournaments/models.py:55-56`.

`Tournament` в `Tour` — `null=True, blank=True`, но `__str__` обращается к
`self.tournament.title` без проверки.

**Факт.** `AttributeError` при `str(Tour(tournament=None))`; ломает админку/шаблоны.
**Ожидаемо.** Строка вида `"3-й тур"` без названия турнира.

**Тест:** `tournaments/tests.py::TestTour::test_str_without_tournament_fails`.

---

## BUG-017. `calculate_resultes` считает отменённый матч

**Где:** `tournaments/models.py:157-190`.

Метод не проверяет `is_canceled`/`is_finished`; при прямом вызове или из
`calculate_statistics` отменённый матч меняет статистику.

**Ожидаемо.** Для отменённого/несыгранного матча статистика не меняется.

**Тест:** `tournaments/tests.py::TestMatchTour::test_calculate_resultes_counts_canceled_match`.

---

## BUG-018. Форма добавления тура падает при `resolver_match=None`

**Где:** `tournaments/admin.py:84-99`.

```python
tour_id = request.resolver_match.kwargs.get("object_id")
```

При открытии формы добавления (`object_id` ещё нет) `resolver_match` может
быть `None` → `AttributeError` вместо пустого queryset.

**Ожидаемо.** `field.queryset.none()` без падения.

**Тест:** `tournaments/tests.py::TestTournamentsAdmin::test_formfield_for_foreignkey_without_resolver_match`.

---

## BUG-019. `start_time=None` роняет главную

**Где:** `fckuban/views.py:44`.

```python
if match.start_time.date() >= now:
```

`Match.start_time` объявлен `null=True, blank=True`. Для матча без времени
получаем `AttributeError` и HTTP 500 на главной/в календаре.

**Ожидаемо.** Пропускать матчи без `start_time` или считать их будущими.

**Тест:** `fckuban/tests.py::TestGetCalendarMatches::test_match_without_start_time_fails`.

---

## BUG-020. В теге календаря не импортирован `Match`

**Где:** `fckuban/templatetags/calendar.py:11-17`.

```python
def get_calendar():
    return Tournament.objects.filter(in_calendar=True).prefetch_related(
        Prefetch('match', queryset=Match.objects.filter(is_active=True))
    )
```

В модуле нет `from calendar_matches.models import Match` (импорт закомментирован
ниже в файле). Любое использование тега `{% calendar_tournaments %}` или
`get_calendar()` даёт `NameError`.

**Ожидаемо.** Импорт `Match` и корректный queryset.

**Тесты:** `fckuban/tests.py::TestTemplateTags::test_calendar_tournaments_tag`,
`test_module_get_calendar_fails`.

---

## BUG-021. `image_path` не работает на Python 3

**Где:** `fckuban/utils.py:12`.

```python
instance_id_hash = md5(str(instance.id)).hexdigest()
```

`hashlib.md5` требует `bytes`, а передаётся `str` → `TypeError: Unicode-objects
must be encoded before hashing`. Вторая строка уже кодирует имя файла, а первая —
нет.

**Ожидаемо.** `md5(str(instance.id).encode('utf-8'))`.
**Использование.** Сейчас функция не подключена к `upload_to`, но при
подключении любой upload упадёт.

**Тест:** `fckuban/tests.py::TestUtils::test_image_path_fails_with_str_digest`.

---

## BUG-022. Тег `current_tournament` выводит `None`

**Где:** `fckuban/templatetags/calendar.py:34`.

`simple_tag` возвращает `None`, когда текущего турнира нет; Django рендерит
`None` как строку `"None"`.

**Ожидаемо.** Пустая строка.
**Тест:** `fckuban/tests.py::TestTemplateTags::test_current_tournament_tag_without_tournament`.

---

## BUG-023. Свежая БД не создаётся: миграция импортирует живую модель

**Где:** `team/migrations/0007_auto_20190509_2142.py:4,8`.

```python
from team.models import BaseTeamMember

def all_teammember_slug(apps, schema_editor):
    all_team_members = BaseTeamMember.objects.all()
```

Миграция должна брать историческую модель через
`apps.get_model('team', 'BaseTeamMember')`, а не импортировать текущую.
Историческая схема на шаге 0007 ещё не содержит `image_hover` (поле добавляется
в 0008), поэтому запрос падает:

```
django.db.utils.OperationalError: no such column: team_baseteammember.image_hover
```

**Факт.** `venv/bin/python manage.py test` (и `migrate` на чистой БД) не может
создать тестовую БД; ни один тест не запускается.
**Временное решение в тестах.** В `pytest.ini` стоит `--nomigrations`:
таблицы создаются из текущих моделей, юнит-тесты работают. Это **не** решение
для продакшена: перед обновлением миграцию нужно исправить (не в рамках
текущей задачи «код не трогаем»).

**Проверка после исправления.**
```bash
venv/bin/python manage.py migrate
venv/bin/python -m pytest   # без --nomigrations
```

---

## BUG-024. Захардкоженная локаль в `check_today`

**Где:** `birthdays/views.py:20`.

```python
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
```

В минимальных Docker/CI-образах локали `ru_RU.UTF-8` может не быть —
`locale.Error` приведёт к 500 на всех страницах, где выводится дата
(главная, новости, календарь, таблица).

**Ожидаемо.** Не зависеть от системной локали (например, статический список
русских месяцев/`django.utils.formats`).

**Тест:** `birthdays/tests.py::TestBirthdayViews::test_check_today_requires_system_locale`.

---

## Что ещё стоит учесть до обновления (не ошибки, найденные тестами)

1. **`SECRET_KEY` захардкожен** в `fckuban/settings.py:24`. По AGENTS.md это
   нарушение: нужен `django-environ`/`.env`. При обновлении Django менять
   настройки безопасности обязательно.
2. **`pymysql.install_as_MySQLdb()`** вызывается на уровне `settings.py`
   (`fckuban/settings.py:14-15`). Для Django 5.x нужен поддерживаемый драйвер
   (`mysqlclient`/`PyMySQL` с актуальной версией) и проверка `mysqlclient` vs
   `pymysql`.
3. **`USE_L10N`** (`fckuban/settings.py`) удалён в Django 5.0; параметр нужно
   убрать.
4. **`python manage.py pytest`** из AGENTS.md не существует: management-команды
   `pytest` в проекте нет. Используйте `python -m pytest` (или добавьте
   `pytest-django`-команду отдельно).
5. **Зависимости `django-ckeditor==5.6.1`, `django-embed-video==1.1.2`,
   `sorl-thumbnail==12.4.1`, `Pillow==5.2.0`** не совместимы с Django 5.x/Python
   3.14; их нужно обновлять вместе с Django. Тесты используют `get_thumbnail`
   с моком, поэтому API sorl проверен только частично.
6. **`AppConfig`** (BUG-003) после Django 3.2 начнёт применяться автоматически —
   проверьте, что русские `verbose_name` не сломали ожидания админки.
7. **`AdminImageWidget.render`** (`news/admin.py:13`) переопределён без
   параметра `renderer`, появившегося в сигнатуре `Widget.render` начиная с
   Django 2.1. На Django 5.x форма админки может упасть с `TypeError`
   (`unexpected keyword argument 'renderer'`). Это нужно проверить и поправить
   при обновлении.
8. **`allow_tags`** (`banner/admin.py:20`) удалён в новых Django: метод
   `show_banner` возвращает сырой HTML, и без `format_html`/`mark_safe` он будет
   экранироваться. Тест `test_show_banner_allow_tags` фиксирует текущее
   поведение, но после обновления его ожидания изменятся.
9. **N+1/дублирование:** `get_calendar()` делает `prefetch_related`, но
   `get_calendar_matches()` вызывает `tournament.match.all().order_by(...)`,
   что сбрасывает prefetch; также блок маппинга соцсетей продублирован в
   `fckuban/views.py`, `news/views.py`, `medialinks/views.py`,
   `partners/views.py`, `tournaments/views.py` (в дочерних view нет ветки
   `twitter`, хотя в `MainView` она есть). Это не функциональные баги, но
   кандидаты на рефакторинг после стабилизации тестов.

---

## Как устроены тесты

- `pytest.ini` — `DJANGO_SETTINGS_MODULE=fckuban.test_settings`,
  `python_files = tests.py test_*.py`, `--nomigrations` (см. BUG-023).
- `fckuban/test_settings.py` — изолированная SQLite `:memory:`, временный
  `MEDIA_ROOT`, быстрый хешер паролей; боевые `fckuban/settings.py` не менялись.
- `.coveragerc` — исключены миграции, `__pycache__`, тесты, `wsgi.py`,
  виртуальные окружения; включено branch-покрытие.
- `conftest.py` — общие фикстуры (`image_file`, `admin_user`, `staff_user`,
  `regular_user`).
- Тесты лежат в `*/tests.py` (там, где эти файлы уже были), плюс новый
  `fckuban/tests.py` для ядра.
- В местах найденных дефектов тест **не падает**: либо ловит текущее исключение,
  либо проверяет текущее поведение, а строка с правильным ожиданием
  закомментирована и помечена `БАГ-NNN`. После исправления дефекта достаточно
  раскомментировать эту строку.
