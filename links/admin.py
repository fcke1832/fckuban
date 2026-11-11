from django.contrib import admin
from django.utils.html import format_html
from sorl.thumbnail import get_thumbnail

from .models import Hashtag, MapsLink, SocialNetworkLink, VKVideo, YoutubeLink


@admin.register(YoutubeLink)
class YoutubeLinkAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "on_main",
        "date_pub",
    )
    list_editable = ("on_main",)
    list_filter = (
        "on_main",
        "date_pub",
    )


@admin.register(VKVideo)
class VKVideoAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "on_main",
        "is_published",
        "date_pub",
    )
    list_editable = (
        "on_main",
        "is_published",
    )
    list_filter = (
        "on_main",
        "is_published",
        "date_pub",
    )
    search_fields = (
        "title",
        "description",
        "link",
    )
    readonly_fields = ("preview_thumbnail",)

    @admin.display(description="Превью")
    def preview_thumbnail(self, obj: VKVideo) -> str:
        """Миниатюра превью в админке."""
        if not obj.preview:
            return "—"
        image = get_thumbnail(obj.preview, "120x68", crop="center", quality=90)
        return format_html('<img src="{}" alt="" width="120" height="68">', image.url)


@admin.register(SocialNetworkLink)
class SocialNetworkLinkAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "link",
    )
    list_editable = ("link",)
    list_filter = (
        "name",
        "link",
    )


@admin.register(MapsLink)
class MapsLinkAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "iframe",
        "is_active",
    )
    list_editable = (
        "iframe",
        "is_active",
    )
    list_filter = (
        "name",
        "iframe",
        "is_active",
    )


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
    )
    list_editable = ("is_active",)
    list_filter = (
        "name",
        "is_active",
    )
