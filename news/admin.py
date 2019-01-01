from sorl.thumbnail import get_thumbnail

from django.contrib import admin
from django.utils.html import format_html

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_pub', 'published', 'is_periodic')
    list_filter = ('date_pub', 'published')
    list_editable = ('published', 'is_periodic')
    fields = (
        'title',  'image', 'photo_thumbnail',
        'published', 'is_periodic', 'date_pub', 'news_text'
    )
    readonly_fields = ('photo_thumbnail',)

    def photo_thumbnail(self, obj):
        if obj.image:
            im = get_thumbnail(obj.image, '750x400', quality=99)
            return format_html(
                    '<img src="{}" border="0" alt="" width="{}" height="{}" />',
                    im.url, im.width, im.height)
        else:
            return ''

    photo_thumbnail.short_description = 'Главное фото'
