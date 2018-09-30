from django.views.generic import ListView
from django.views.generic.detail import DetailView
from .models import News


class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'
    context_object_name = 'news_list'

    def get_queryset(self):
        return News.objects.filter(published=True).order_by('-date_pub')[:8]


class NewsDetailView(DetailView):
    model = News
    template_name = 'news_detail.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super(NewsDetailView, self).get_context_data(**kwargs)
        context['another_news'] = News.objects.filter(published=True).exclude(id=self.object.id).order_by('-date_pub')[:3]
        return context