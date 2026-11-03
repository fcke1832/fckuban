"""Тесты приложения seo."""
import pytest
from django.contrib import admin

import seo.views  # noqa: F401  (пустой views.py должен импортироваться)
from seo.admin import SeoDataAdmin
from seo.apps import SeoConfig
from seo.models import SeoData


class TestSeoConfig:
    def test_app_config(self):
        assert SeoConfig.name == 'seo'


@pytest.mark.django_db
class TestSeoDataModel:
    def test_str_returns_title(self):
        seo = SeoData.objects.create(title='ФК Кубань')
        assert str(seo) == 'ФК Кубань'

    def test_fields_are_optional(self):
        seo = SeoData.objects.create()
        assert seo.title == ''
        assert seo.description == ''
        assert seo.keywords == ''

    def test_meta_verbose_names(self):
        assert SeoData._meta.verbose_name == 'SEO'
        assert SeoData._meta.verbose_name_plural == 'SEO'


@pytest.mark.django_db
class TestSeoDataAdmin:
    def test_registered(self):
        assert SeoData in admin.site._registry
        assert isinstance(admin.site._registry[SeoData], SeoDataAdmin)

    def test_list_display(self):
        model_admin = SeoDataAdmin(SeoData, admin.site)
        assert model_admin.list_display == ('title',)
