from django.contrib import admin
from .models import BirthdayItem


@admin.register(BirthdayItem)
class BirthdayItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'second_name', 'date_of_birth',)
    list_filter = ('name', 'second_name', 'date_of_birth',)
    # list_editable = ('name', 'second_name','date_of_birth',)
