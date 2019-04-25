from sorl.thumbnail import get_thumbnail

from django.contrib import admin
from django.utils.html import format_html

from .models import Partner


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('title', 'type_partner', 'number', 'is_active')
    list_filter = ('title', 'type_partner', 'number', 'is_active')
    list_editable = ('is_active', 'number', )
    fields = (
        'title', 'type_partner',
        'image', 'logo_thumbnail',
        'link', 'description',
        'is_active',
    )
    readonly_fields = ('logo_thumbnail',)

    def logo_thumbnail(self, obj):
        if obj.image:
            im = get_thumbnail(obj.image, '70x70', quality=99)
            return format_html(
                    '<img src="{}" border="0" alt="" width="{}" height="{}" />',
                    im.url, im.width, im.height)
        else:
            return ''

    logo_thumbnail.short_description = 'Логотип'
