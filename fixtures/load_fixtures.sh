#!/usr/bin/env bash
#
# Загрузка фикстур проекта ФК «Кубань».
#
# Запуск (из корня проекта или из любой папки — скрипт сам перейдёт в корень):
#   ./fixtures/load_fixtures.sh
#   python -m pip install ...  # не требуется, используется текущее окружение
#
# Переменные окружения:
#   PYTHON  — интерпретатор (по умолчанию .venv/bin/python, если он есть, иначе python)
#   DB      — переопределить БД не получится, используется DATABASES из настроек
#
# Порядок файлов важен: сначала турниры/туры/команды, затем всё, что ссылается на них.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -z "${PYTHON:-}" ]; then
    if [ -x "$PROJECT_ROOT/.venv/bin/python" ]; then
        PYTHON="$PROJECT_ROOT/.venv/bin/python"
    else
        PYTHON="python"
    fi
fi

FIXTURES=(
    "fixtures/tournaments.json"
    "fixtures/team.json"
    "fixtures/partners.json"
    "fixtures/news.json"
    "fixtures/medialinks.json"
    "fixtures/calendar_matches.json"
    "fixtures/birthdays.json"
    "fixtures/banner.json"
)

# 1. Изображения-заглушки: ImageField читает файлы из MEDIA_ROOT,
#    поэтому копируем их из fixtures/images в media/fixtures.
#    В фикстурах имя файла записано относительно MEDIA_ROOT: fixtures/news/news-1.png
#    (полный путь — media/fixtures/news/news-1.png).
mkdir -p media/fixtures
cp -R fixtures/images/. media/fixtures/

# 2. Загрузка самих данных.
"$PYTHON" manage.py loaddata "${FIXTURES[@]}"

# 3. Короткий отчёт о количестве загруженных объектов.
"$PYTHON" manage.py shell -c "
from django.apps import apps

pairs = [
    ('tournaments', 'Tournament'), ('tournaments', 'Tour'),
    ('tournaments', 'Team'), ('tournaments', 'MatchTour'),
    ('team', 'Player'), ('team', 'Coach'),
    ('partners', 'Partner'),
    ('news', 'News'), ('news', 'NewsHashTag'), ('news', 'NewsImage'),
    ('medialinks', 'Article'),
    ('calendar_matches', 'Match'),
    ('birthdays', 'BirthdayItem'),
    ('banner', 'Banner'),
]
for app_label, model_name in pairs:
    model = apps.get_model(app_label, model_name)
    print(f'{app_label}.{model_name}: {model.objects.count()}')
"
