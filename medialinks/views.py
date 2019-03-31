from links.models import SocialNetworkLink
from fckuban.views import get_calendar, get_calendar_matches
from birthdays.views import today_birtdays, check_today
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .models import Article


class ArticlesListView(ListView):
    model = Article
    template_name = 'media_list.html'
    context_object_name = 'articles_list'

    def get_queryset(self):
        return Article.objects.filter(published=True).order_by('-date_pub')

    def get_context_data(self, **kwargs):
        context = super(ArticlesListView, self).get_context_data(**kwargs)
        calendar_tournaments = get_calendar()
        calendar_matches, futured_calendar_matches = get_calendar_matches(calendar_tournaments)
        context['calendar_matches'] = sorted(calendar_matches, key=lambda instance: instance.start_time)
        context['birthdays'] = today_birtdays()
        context['today_date'] = check_today()
        try:
            context['future_match'] = (sorted(futured_calendar_matches, key=lambda instance: instance.start_time))[0]
        except IndexError:
            context['future_match'] = context['calendar_matches'][-1]
        social_networks_links = SocialNetworkLink.objects.all()
        if social_networks_links:
            for link in social_networks_links:
                if 'www.facebook.com/' in link.link:
                    context['facebook_link'] = link.link
                elif 'https://vk.com/' in link.link:
                    context['vk_link'] = link.link
                elif 'www.instagram.com' in link.link:
                    context['instagram_link'] = link.link
                elif 'www.youtube.com' in link.link:
                    context['youtube_channel'] = link.link
                elif 'https://t.me/' in link.link:
                    context['telegram_channel'] = link.link
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        calendar_tournaments = get_calendar()
        calendar_matches, futured_calendar_matches = get_calendar_matches(calendar_tournaments)
        context['calendar_matches'] = sorted(calendar_matches, key=lambda instance: instance.start_time)
        context['birthdays'] = today_birtdays()
        context['today_date'] = check_today()
        try:
            context['future_match'] = (sorted(futured_calendar_matches, key=lambda instance: instance.start_time))[0]
        except IndexError:
            context['future_match'] = context['calendar_matches'][-1]
        social_networks_links = SocialNetworkLink.objects.all()
        if social_networks_links:
            for link in social_networks_links:
                if 'www.facebook.com/' in link.link:
                    context['facebook_link'] = link.link
                elif 'https://vk.com/' in link.link:
                    context['vk_link'] = link.link
                elif 'www.instagram.com' in link.link:
                    context['instagram_link'] = link.link
                elif 'www.youtube.com' in link.link:
                    context['youtube_channel'] = link.link
                elif 'https://t.me/' in link.link:
                    context['telegram_channel'] = link.link
        return context
