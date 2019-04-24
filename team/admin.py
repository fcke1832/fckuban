from sorl.thumbnail import get_thumbnail
from django.contrib import admin
from django.utils.html import format_html

from .models import Player, Coach


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    list_filter = ('full_name',)
    fields = (
        'full_name', 'image', 'photo_thumbnail', 'number',
        'birthday', 'position', 'weight', 'growth',
    )
    readonly_fields = ('photo_thumbnail',)

    def photo_thumbnail(self, obj):
        if obj.image:
            im = get_thumbnail(obj.image, '150x250', quality=99)
            return format_html(
                    '<img src="{}" border="0" alt="" width="{}" height="{}" />',
                    im.url, im.width, im.height)
        else:
            return ''

    photo_thumbnail.short_description = 'Фото'


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    list_filter = ('full_name',)
    fields = (
        'full_name', 'image',
        'photo_thumbnail', 'birthday',
    )
    readonly_fields = ('photo_thumbnail',)

    def photo_thumbnail(self, obj):
        if obj.image:
            im = get_thumbnail(obj.image, '150x250', quality=99)
            return format_html(
                    '<img src="{}" border="0" alt="" width="{}" height="{}" />',
                    im.url, im.width, im.height)
        else:
            return ''

    photo_thumbnail.short_description = 'Фото'
