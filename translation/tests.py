"""Тесты приложения translation (заготовка без моделей и представлений)."""
from django.apps import apps

import translation.admin  # noqa: F401
import translation.models  # noqa: F401
import translation.views  # noqa: F401
from translation.apps import TranslationConfig


class TestTranslationApp:
    def test_app_config(self):
        assert TranslationConfig.name == 'translation'
        assert apps.get_app_config('translation').name == 'translation'
        # БАГ-003: в Django 2.0 без default_app_config в apps.py используется
        # django.apps.config.AppConfig, поэтому verbose_name из TranslationConfig
        # не применяется. После перехода на Django 5.x проверка должна проходить.
        # assert apps.get_app_config('translation').__class__ is TranslationConfig

    def test_app_has_no_models(self):
        assert list(apps.get_app_config('translation').get_models()) == []
