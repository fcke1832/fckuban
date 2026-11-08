"""Тесты приложения tickets."""
import pytest
from django.contrib import admin
from django.urls import reverse

from tickets.admin import (
    SectorInline,
    TicketProgramAdmin,
    TicketSaleWidgetAdmin,
    TribuneAdmin,
    TribuneInline,
)
from tickets.apps import TicketsConfig
from tickets.models import Sector, TicketProgram, TicketSaleWidget, Tribune
from tickets.views import TicketSaleView


class TestTicketsConfig:
    def test_app_config(self):
        assert TicketsConfig.name == 'tickets'


@pytest.mark.django_db
class TestTicketProgram:
    def test_str(self):
        program = TicketProgram.objects.create(name='Сезон 2024')
        assert str(program) == 'Сезон 2024'

    def test_meta_verbose_names(self):
        assert TicketProgram._meta.verbose_name == 'Билетная программа'
        assert TicketProgram._meta.verbose_name_plural == 'Билетные программы'


@pytest.mark.django_db
class TestTribune:
    def test_str(self):
        program = TicketProgram.objects.create(name='Сезон 2024')
        tribune = Tribune.objects.create(name='Запад', ticket_program=program)
        assert str(tribune) == 'Запад'

    def test_default_is_not_on_sale(self):
        program = TicketProgram.objects.create(name='Сезон 2024')
        tribune = Tribune.objects.create(name='Запад', ticket_program=program)
        assert tribune.is_sale is False

    def test_related_name_tribunes(self):
        program = TicketProgram.objects.create(name='Сезон 2024')
        Tribune.objects.create(name='Запад', ticket_program=program)
        Tribune.objects.create(name='Восток', ticket_program=program)
        assert program.tribunes.count() == 2

    def test_cascade_delete(self):
        program = TicketProgram.objects.create(name='Сезон 2024')
        Tribune.objects.create(name='Запад', ticket_program=program)
        program.delete()
        assert Tribune.objects.count() == 0


@pytest.mark.django_db
class TestSector:
    def test_str(self):
        program = TicketProgram.objects.create(name='Сезон 2024')
        tribune = Tribune.objects.create(name='Запад', ticket_program=program)
        sector = Sector.objects.create(name='101', price='500', tribune=tribune)
        assert str(sector) == '101'

    def test_default_is_not_on_sale(self):
        program = TicketProgram.objects.create(name='Сезон 2024')
        tribune = Tribune.objects.create(name='Запад', ticket_program=program)
        sector = Sector.objects.create(name='101', price='500', tribune=tribune)
        assert sector.is_sale is False

    def test_cascade_delete(self):
        program = TicketProgram.objects.create(name='Сезон 2024')
        tribune = Tribune.objects.create(name='Запад', ticket_program=program)
        Sector.objects.create(name='101', price='500', tribune=tribune)
        tribune.delete()
        assert Sector.objects.count() == 0


@pytest.mark.django_db
class TestTicketSaleWidget:
    def test_default_is_active(self):
        widget = TicketSaleWidget.objects.create(link='https://tickets.example.com/')
        assert widget.is_active is True

    def test_meta_verbose_names(self):
        assert TicketSaleWidget._meta.verbose_name == (
            'Ссылка на виджет онлайн-продажи билетов'
        )


@pytest.mark.django_db
class TestTicketSaleView:
    def test_context_without_widget(self, client):
        response = client.get(reverse('tickets:ticket_sale'))
        assert response.status_code == 200
        assert response.context['link_buy_tickets'] is None
        assert response.context['is_tickets'] is True

    def test_context_with_widget(self, client):
        TicketSaleWidget.objects.create(link='https://tickets.example.com/')
        response = client.get(reverse('tickets:ticket_sale'))
        assert response.status_code == 200
        assert response.context['link_buy_tickets'] == 'https://tickets.example.com/'

    def test_template_used(self, client):
        response = client.get(reverse('tickets:ticket_sale'))
        assert 'ticket_sale.html' in [t.name for t in response.templates]

    def test_get_context_data_directly(self, rf):
        view = TicketSaleView()
        view.request = rf.get('/tickets/sale')
        context = view.get_context_data()
        assert context['link_buy_tickets'] is None


@pytest.mark.django_db
class TestTicketsAdmin:
    def test_inlines(self):
        assert SectorInline.model is Sector
        assert TribuneInline.model is Tribune
        assert SectorInline.extra == 1
        assert TribuneInline.extra == 0

    def test_tribune_admin(self):
        model_admin = TribuneAdmin(Tribune, admin.site)
        assert model_admin.list_display == ('name', 'is_sale')
        assert model_admin.list_filter == ('name', 'is_sale')
        assert model_admin.list_editable == ('is_sale',)
        assert model_admin.inlines == [SectorInline]
        assert Tribune in admin.site._registry

    def test_ticket_program_admin(self):
        model_admin = TicketProgramAdmin(TicketProgram, admin.site)
        assert model_admin.list_display == ('name',)
        assert model_admin.list_filter == ('name',)
        assert model_admin.inlines == [TribuneInline]
        assert TicketProgram in admin.site._registry

    def test_sale_widget_admin(self):
        model_admin = TicketSaleWidgetAdmin(TicketSaleWidget, admin.site)
        assert model_admin.list_display == ('link', 'is_active')
        assert model_admin.list_editable == ('is_active',)
        assert TicketSaleWidget in admin.site._registry
