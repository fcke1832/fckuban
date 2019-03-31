from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_pub', 'sourse_name', 'published',)
    list_filter = ('date_pub', 'published')
    list_editable = ('published', )
    fields = (
        'title', 'sourse_name', 'sourse',
        'image', 'published', 'date_pub', 'news_text'
    )
