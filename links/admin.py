from django.contrib import admin
from .models import YoutubeLink, SocialNetworkLink, MapsLink


@admin.register(YoutubeLink)
class YoutubeLinkAdmin(admin.ModelAdmin):
    list_display = ('description', 'on_main', 'date_pub',)
    list_editable = ('on_main',)
    list_filter = ('on_main', 'date_pub',)


@admin.register(SocialNetworkLink)
class SocialNetworkLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'link',)
    list_editable = ('link',)
    list_filter = ('name', 'link',)


@admin.register(MapsLink)
class MapsLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'is_active',)
    list_editable = ('link', 'is_active',)
    list_filter = ('name', 'link', 'is_active',)