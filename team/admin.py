from django.contrib import admin

from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    list_filter = ('full_name',)
    # fields = (
    #     'title',  'image', 'photo_thumbnail', 'crop_image', 'crop_image_detail_page',
    #     'published', 'is_periodic', 'date_pub', 'news_text'
    # )
