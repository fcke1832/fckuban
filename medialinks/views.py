from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .models import Article


class ArticlesListView(ListView):
    model = Article
    template_name = 'media_list.html'
    context_object_name = 'articles_list'

    def get_queryset(self):
        print(Article.objects.filter(published=True))
        return Article.objects.filter(published=True).order_by('-date_pub')
