from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_pub', 'sourse_name', 'published', 'is_image',)
    list_filter = ('date_pub', 'published',)
    list_editable = ('published', 'is_image',)
    fields = (
        'title', 'sourse_name', 'sourse',
        'image', 'is_image', 'published',
        'date_pub', 'news_text'
    )
