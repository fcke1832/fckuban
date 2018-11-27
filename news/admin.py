from django.contrib import admin
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_pub', 'published', 'is_periodic')
    list_filter = ('date_pub', 'published')
    list_editable = ('published', 'is_periodic')
