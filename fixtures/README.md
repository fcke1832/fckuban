# Фикстуры проекта ФК «Кубань»

Демонстрационные данные для наполнения моделей:

| Файл | Модели |
| --- | --- |
| `tournaments.json` | `Tournament`, `Tour`, `Team`, `MatchTour` |
| `team.json` | `Player`, `Coach` |
| `partners.json` | `Partner` |
| `news.json` | `NewsHashTag`, `News`, `NewsImage` |
| `medialinks.json` | `Article` |
| `calendar_matches.json` | `Match` |
| `birthdays.json` | `BirthdayItem` |
| `banner.json` | `Banner` |

Изображения-заглушки лежат в `fixtures/images/` (по одной картинке на объект).
В фикстурах путь записан относительно `MEDIA_ROOT`, например `fixtures/news/news-1.png`,
поэтому файл должен лежать в `media/fixtures/news/news-1.png` — перед загрузкой картинки туда копируются.

## 1. Быстрый запуск (одна команда)

Из корня проекта (там, где лежит `manage.py`), после `uv sync` и `uv run python manage.py migrate`:

```bash
./fixtures/load_fixtures.sh
```

Скрипт копирует картинки, загружает все фикстуры в правильном порядке и печатает количество созданных объектов.
Интерпретатор можно переопределить: `PYTHON=.venv/bin/python ./fixtures/load_fixtures.sh`.

Пользователей фикстуры не создают: для входа в `/admin/` выполните
`uv run python manage.py createsuperuser`.

## 2. Запуск вручную

Подготовить изображения (один раз):

```bash
mkdir -p media/fixtures
cp -R fixtures/images/. media/fixtures/
```

Загрузить все фикстуры одной командой (порядок файлов важен, файлы перечислены явно):

```bash
uv run python manage.py loaddata \
    fixtures/tournaments.json \
    fixtures/team.json \
    fixtures/partners.json \
    fixtures/news.json \
    fixtures/medialinks.json \
    fixtures/calendar_matches.json \
    fixtures/birthdays.json \
    fixtures/banner.json
```

Так как `fixtures/` добавлен в `FIXTURE_DIRS` (`fckuban/settings.py`), те же данные можно загрузить по коротким именам:

```bash
uv run python manage.py loaddata tournaments team partners news medialinks calendar_matches birthdays banner
```

## 3. Загрузка одного приложения

```bash
uv run python manage.py loaddata fixtures/tournaments.json   # турниры, туры, команды, матчи туров
uv run python manage.py loaddata fixtures/team.json          # игроки и тренерский штаб
uv run python manage.py loaddata fixtures/partners.json      # партнёры и спонсоры
uv run python manage.py loaddata fixtures/news.json          # хештэги, новости, фото слайдера
uv run python manage.py loaddata fixtures/medialinks.json    # статьи из СМИ
uv run python manage.py loaddata fixtures/calendar_matches.json  # календарь матчей
uv run python manage.py loaddata fixtures/birthdays.json     # именинники
uv run python manage.py loaddata fixtures/banner.json        # баннеры
```

`calendar_matches.json` ссылается на `Team` и `Tournament`, поэтому загружайте его **после** `tournaments.json`.

## 4. Повторная загрузка и очистка

Загрузка идемпотентна по `pk`: повторный `loaddata` обновляет существующие объекты, а не создаёт дубликаты.
Если нужен полностью чистый набор данных:

```bash
# локальная SQLite-база создаётся заново
rm -f db.sqlite3
uv run python manage.py migrate
./fixtures/load_fixtures.sh
```

Не хотите удалять базу — удалите только объекты фикстур через `uv run python manage.py shell` или админку
(`flush` очистит вообще все данные, включая пользователей).

## 5. Проверка результата

```bash
uv run python manage.py shell -c "
from tournaments.models import Tournament, Team, MatchTour
from team.models import Player, Coach
from news.models import News, NewsHashTag, NewsImage
from medialinks.models import Article
from calendar_matches.models import Match
from partners.models import Partner
from birthdays.models import BirthdayItem
from banner.models import Banner
print('турниров:', Tournament.objects.count())
print('команд:', Team.objects.count())
print('матчей туров:', MatchTour.objects.count())
print('игроков:', Player.objects.count(), 'тренеров:', Coach.objects.count())
print('новостей:', News.objects.count(), 'хештэгов:', NewsHashTag.objects.count(), 'фото:', NewsImage.objects.count())
print('статей:', Article.objects.count(), 'матчей календаря:', Match.objects.count())
print('партнёров:', Partner.objects.count(), 'именинников:', BirthdayItem.objects.count(), 'баннеров:', Banner.objects.count())
"
```

Пересчитать турнирную таблицу по загруженным `MatchTour` (значения в `Team` уже согласованы с результатами матчей):

```bash
uv run python manage.py shell -c "
from tournaments.models import Tournament
Tournament.objects.get(pk=1).calculate_statistics()
"
```

## 6. Что внутри

* **Турниры** — три турнира, основной (`on_main=True`, `in_calendar=True`) — «Вторая лига «Б», группа 1 (сезон 2026/2027)».
* **Туры** — 4 тура основного турнира, 1 тур Кубка России и 1 неактивный тур товарищеских матчей.
* **Команды** — 8 команд с логотипами, статистика (`points`, `matches`, `goals_*`, `position_number`) согласована с результатами `MatchTour`.
* **Матчи туров** — 12 завершённых матчей (туры 1–3) и 4 будущих матча 4-го тура.
  У будущих матчей `is_active=False` («Включить в таблицу»), чтобы `Tournament.calculate_statistics()` не считал их нулевой ничьей.
* **Игроки** — 10 футболистов всех амплуа с номерами, ростом, весом и датами рождения; **тренеры** — 3 человека (главный, старший, тренер вратарей).
  `Player` и `Coach` наследуются от конкретной модели `BaseTeamMember` (multi-table inheritance), поэтому в `team.json`
  сначала идут строки `team.baseteammember`, а затем `team.player` / `team.coach` с тем же `pk`.
* **Партнёры** — 4 записи: спонсоры и партнёры, одна неактивная.
* **Новости** — 4 новости (3 опубликованные и 1 отложенная: `is_periodic=True`, `published=False`), 5 хештэгов, 4 фото слайдера.
* **Статьи из СМИ** — 2 статьи с источниками.
* **Календарь матчей** — 6 матчей: 3 прошедших и 3 будущих, у одного из будущих `time_invisible=True`.
* **Именинники** — 5 записей, у одной (`Виктор Панов`) дата рождения 4 ноября — попадает в виджет «с днём рождения» при загрузке в начале ноября.
* **Баннеры** — 2 записи, опубликован один (он и показывается на главной).

## 7. Примечания

* Поле `Match.ticket_program` оставлено пустым (`null`): в наборе нет `TicketProgram`.
  Если нужна билетная программа — создайте её в админке и привяжите матчи, либо добавьте в `calendar_matches.json` запись `tickets.ticketprogram` с тем же `pk`, что в `ticket_program`.
* Все изображения — сгенерированные заглушки (green/yellow в стиле клуба), их можно заменить реальными через админку.
  Имя файла в `ImageField` задано относительно `MEDIA_ROOT` (`fixtures/...`), поэтому превью доступны по адресу
  `/media/fixtures/...`; префикс `media/` из `upload_to` в моделях здесь не дублируется.
* Даты указаны в часовом поясе `Europe/Moscow` (`+03:00`) и корректно сохраняются при `USE_TZ=True`.
* `slug` новостей и статей задан явно, поэтому `loaddata` не конфликтует с автогенерацией в `News.save()` / `Article.save()`
  (при `loaddata` методы `save()` не вызываются).
