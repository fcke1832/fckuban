from itertools import chain

from django.views.generic import ListView, View, TemplateView
from news.models import  News
from tournaments.models import Tournament, Team
from links.models import YoutubeLink, SocialNetworkLink
from calendar_matches.models import Match

class MainView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_qs'] = News.objects.filter(published=True).order_by('-date_pub')[:4]

        current_tournament = Tournament.objects.filter(on_main=True).first()
        if current_tournament:
            context['current_tournament'] = current_tournament
            context['teams'] = current_tournament.team.filter(is_active=True).order_by('-points')

        youtube_link = YoutubeLink.objects.filter(on_main=True).first()
        if youtube_link:
            context['youtube_link'] = youtube_link
        social_networks_links = SocialNetworkLink.objects.all()
        if social_networks_links:
            for link in social_networks_links:
                if 'www.facebook.com/' in link.link:
                    context['facebook_link'] = link.link
                elif 'https://vk.com/' in link.link:
                    context['vk_link'] = link.link
                elif 'www.instagram.com' in link.link:
                    context['instagram_link'] = link.link

        fcke_team = Team.objects.filter(is_fcke=True).first()
        home_matches = Match.objects. filter(tournament=current_tournament, home_team=fcke_team)
        guest_matches = Match.objects. filter(tournament=current_tournament, guest_team=fcke_team)
        context['home_matches'] = home_matches
        context['guest_matches'] = guest_matches
        fcke_matches_list = sorted(chain(home_matches, guest_matches), key=lambda instance: instance.start_time)
        context['fcke_matches_list'] = fcke_matches_list

        return context
