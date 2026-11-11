"""Настройки Django для запуска тестов (pytest + pytest-django).

Модуль намеренно не меняет ``fckuban.settings``: боевые настройки остаются
как есть до отдельного этапа обновления версий. Здесь только изолированная
тестовая БД, временный MEDIA_ROOT и ускоренные хэшеры паролей.
"""

import os
import tempfile

# .env может отсутствовать в CI: тестам достаточно фиктивного ключа.
os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-secret-key")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "testserver,localhost")

from .settings import *  # noqa: E402,F401,F403

DEBUG = False

# Тесты по умолчанию работают со старой вёрсткой (v1). Тесты нового дизайна
# включают v2 через override_settings(SITE_VERSION='v2').
SITE_VERSION = "v1"
# Тесты работают в v1, где превью остаются PNG (fallback).
THUMBNAIL_FORMAT = "PNG"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    # Отдельная БД взносов: в тестах тоже SQLite, но отдельный алиас.
    "dues": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

MEDIA_ROOT = tempfile.mkdtemp(prefix="fckuban-test-media-")
STATIC_ROOT = os.path.join(MEDIA_ROOT, "static")

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Ошибки шаблонов не должны "съедаться" в тестах.
TEMPLATES[0]["OPTIONS"]["string_if_invalid"] = ""  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Тестовый клиент ходит на localhost.
ALLOWED_HOSTS = ["*"]
