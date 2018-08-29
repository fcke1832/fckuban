from django.views.generic import ListView, View, TemplateView
from news.models import  News


class MainView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_qs'] = News.objects.filter(published=True).order_by('-date_pub')[:4]
        return context
