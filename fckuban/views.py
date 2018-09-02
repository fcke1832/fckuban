from django.views.generic import ListView, View, TemplateView
from news.models import  News
from tournaments.models import Tournament
from links.models import YoutubeLink, SocialNetworkLink

class MainView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_qs'] = News.objects.filter(published=True).order_by('-date_pub')[:4]
        current_tournament = Tournament.objects.filter(on_main=True).first()
        if current_tournament:
            context['current_tournament'] = current_tournament
            context['teams'] = current_tournament.team.filter(is_active=True).order_by('-points')
        context['youtube_link'] = YoutubeLink.objects.filter(on_main=True).first()
        social_networks_links = SocialNetworkLink.objects.all()
        if social_networks_links:
            for link in social_networks_links:
                if 'www.facebook.com/' in link.link:
                    context['facebook_link'] = link.link
                elif 'https://vk.com/' in link.link:
                    context['vk_link'] = link.link
                elif 'www.instagram.com' in link.link:
                    context['instagram_link'] = link.link

        return context
