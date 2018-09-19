from django.views.generic import ListView
from .models import News


class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'
    context_object_name = 'news_list'

    def get_queryset(self):
        return News.objects.filter(published=True).order_by('-date_pub')[:6]