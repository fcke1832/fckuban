from django.contrib import admin
from .models import SeoData


@admin.register(SeoData)
class SeoDataAdmin(admin.ModelAdmin):
    list_display = ('title',)
