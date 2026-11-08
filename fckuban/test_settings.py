"""Настройки Django для запуска тестов (pytest + pytest-django).

Модуль намеренно не меняет ``fckuban.settings``: боевые настройки остаются
как есть до отдельного этапа обновления версий. Здесь только изолированная
тестовая БД, временный MEDIA_ROOT и ускоренные хэшеры паролей.
"""
import os
import tempfile

from .settings import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MEDIA_ROOT = tempfile.mkdtemp(prefix='fckuban-test-media-')
STATIC_ROOT = os.path.join(MEDIA_ROOT, 'static')

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Ошибки шаблонов не должны "съедаться" в тестах.
TEMPLATES[0]['OPTIONS']['string_if_invalid'] = ''  # noqa: F405

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Тестовый клиент ходит на localhost.
ALLOWED_HOSTS = ['*']
