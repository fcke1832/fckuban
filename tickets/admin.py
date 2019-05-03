from django.contrib import admin

from .models import TicketProgram, Tribune, Sector, TicketSaleWidget


class SectorInline(admin.TabularInline):
    model = Sector
    extra = 1


class TribuneInline(admin.TabularInline):
    model = Tribune
    extra = 0


@admin.register(Tribune)
class TribuneAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_sale',)
    list_filter = ('name', 'is_sale',)
    list_editable = ('is_sale',)
    inlines = [SectorInline]


@admin.register(TicketProgram)
class TicketProgramAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    inlines = [TribuneInline]


@admin.register(TicketSaleWidget)
class TicketSaleWidgetAdmin(admin.ModelAdmin):
    list_display = ('link', 'is_active',)
    list_editable = ('is_active',)
