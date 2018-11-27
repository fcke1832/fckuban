from django.contrib import admin
from .models import BirthdayItem


@admin.register(BirthdayItem)
class BirthdayItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth',)
    list_filter = ('name', 'date_of_birth',)
    list_editable = ('date_of_birth',)
