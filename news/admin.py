from sorl.thumbnail import get_thumbnail

from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.forms import ModelForm
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import News, NewsImage, NewsHashTag


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            t = get_thumbnail(value,'100x100')
            output.append('<img src="{}">'.format(t.url))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class NewsImageForm(ModelForm):
    """
    Image Admin Form
    """
    class Meta:
        model = NewsImage
        fields = "__all__"
        widgets = {
            'slider_image' : AdminImageWidget,
        }


@admin.register(NewsHashTag)
class NewsHashTagAdmin(admin.ModelAdmin):
    list_display = ('text',)
    list_filter = ('text',)


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    form = NewsImageForm
    extra = 0


class NewsHashTagInline(admin.TabularInline):
    model = News.hashtags.through
    extra = 1


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_pub', 'published', 'is_periodic')
    list_filter = ('date_pub', 'published')
    list_editable = ('published', 'is_periodic')
    fields = (
        'title',  'image', 'photo_thumbnail', 'crop_image', 'crop_image_detail_page',
        'published', 'is_periodic', 'date_pub', 'news_text'
    )
    readonly_fields = ('photo_thumbnail',)
    inlines = [NewsImageInline, NewsHashTagInline]

    def photo_thumbnail(self, obj):
        if obj.image:
            im = get_thumbnail(obj.image, '750x400', quality=99)
            return format_html(
                    '<img src="{}" border="0" alt="" width="{}" height="{}" />',
                    im.url, im.width, im.height)
        else:
            return ''

    def save_model(self, request, obj, form, change):
        super(NewsAdmin, self).save_model(request, obj, form, change)

        for image in request.FILES.getlist('photos_multiple'):
            obj.slider_images.get_or_create(slider_image=image)

    photo_thumbnail.short_description = 'Главное фото'
