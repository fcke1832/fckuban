"""Общие pytest-фикстуры проекта."""
import locale

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

# Проверяем локаль один раз: в минимальных CI/Docker-образах ru_RU.UTF-8
# может отсутствовать (это отдельный дефект проекта, см. BUGS.md, BUG-024).
try:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    RU_LOCALE_AVAILABLE = True
except locale.Error:
    RU_LOCALE_AVAILABLE = False


@pytest.fixture(autouse=True)
def _safe_locale(monkeypatch):
    """Не даём тестам падать на setlocale, если русской локали нет."""
    if RU_LOCALE_AVAILABLE:
        return
    original_setlocale = locale.setlocale

    def safe_setlocale(category, value=None):
        if value == 'ru_RU.UTF-8':
            return 'C'
        return original_setlocale(category, value)

    monkeypatch.setattr('birthdays.views.locale.setlocale', safe_setlocale)


@pytest.fixture
def ru_locale_available():
    """Признак наличия системной локали ru_RU.UTF-8."""
    return RU_LOCALE_AVAILABLE


# Валидный PNG 1x1 (используется там, где нужен настоящий ImageField).
PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00'
    b'\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
    b'\x00\x00\x00\x00IEND\xaeB`\x82'
)


@pytest.fixture
def image_file():
    """Фабрика SimpleUploadedFile с валидным PNG."""

    def _make(name='test.png'):
        return SimpleUploadedFile(name, PNG_BYTES, content_type='image/png')

    return _make


@pytest.fixture
def admin_user(db):
    """Суперпользователь для проверок админки."""
    return get_user_model().objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin-password',
    )


@pytest.fixture
def staff_user(db):
    """Пользователь штаба (доступ к предпросмотру новостей)."""
    return get_user_model().objects.create_user(
        username='staff',
        password='staff-password',
        is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    """Обычный авторизованный пользователь."""
    return get_user_model().objects.create_user(
        username='regular',
        password='regular-password',
    )
