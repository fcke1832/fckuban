from django.contrib import admin
from .models import YoutubeLink, SocialNetworkLink, MapsLink, Hashtag


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
    list_display = ('name', 'iframe', 'is_active',)
    list_editable = ('iframe', 'is_active',)
    list_filter = ('name', 'iframe', 'is_active',)


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active',)
    list_editable = ('is_active',)
    list_filter = ('name', 'is_active',)
