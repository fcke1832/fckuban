from sorl.thumbnail import get_thumbnail
from django.contrib import admin
from django.utils.html import format_html

from .models import Player, Coach


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birthday',  'position',)
    list_filter = ('full_name', 'birthday',  'position',)
    fields = (
        'full_name', 'birthday',
        'number', 'position',
        'weight', 'growth',
        'image', 'image_thumbnail',
        'image_hover', 'image_hover_thumbnail',
        'image_detail', 'image_detail_thumbnail',
        'image_slider', 'image_slider_thumbnail',
        'slug',
    )
    readonly_fields = ('image_thumbnail', 'image_hover_thumbnail', 'image_detail_thumbnail', 'image_slider_thumbnail',)

    def image_thumbnail(self, obj):
        if obj.image:
            im = get_thumbnail(obj.image, '75x125', quality=99)
            return format_html(
                    '<img src="{}" border="0" alt="" width="{}" height="{}" />',
                    im.url, im.width, im.height)
        else:
            return ''

    def image_hover_thumbnail(self, obj):
        if obj.image_hover:
            im = get_thumbnail(obj.image_hover, '75x125', quality=99)
            return format_html(
                    '<img src="{}" border="0" alt="" width="{}" height="{}" />',
                    im.url, im.width, im.height)
        else:
            return ''

    def image_detail_thumbnail(self, obj):
        if obj.image_detail:
            im = get_thumbnail(obj.image_detail, '75x125', quality=99)
            return format_html(
                    '<img src="{}" border="0" alt="" width="{}" height="{}" />',
                    im.url, im.width, im.height)
        else:
            return ''

    def image_slider_thumbnail(self, obj):
        if obj.image_slider:
            im = get_thumbnail(obj.image_slider, '75x125', quality=99)
            return format_html(
                    '<img src="{}" border="0" alt="" width="{}" height="{}" />',
                    im.url, im.width, im.height)
        else:
            return ''

    image_thumbnail.short_description = 'Фото в списке'
    image_hover_thumbnail.short_description = 'Фото при наведении'
    image_detail_thumbnail.short_description = 'Фото персональной страницы'
    image_slider_thumbnail.short_description = 'Фото в слайдере'


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
