from django.contrib import admin
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.admin import AdminImageMixin

from .models import Banner


@admin.register(Banner)
class BannerAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "published",
    )
    list_filter = ("published",)
    list_editable = ("published",)

    def show_banner(self, obj):
        im = get_thumbnail(obj.image, "125", crop="center", quality=99)
        if im:
            return f'<img src="{im.url}">'

        return ""

    show_banner.allow_tags = True
