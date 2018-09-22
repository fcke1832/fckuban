from itertools import chain

from django.views.generic import ListView, View, TemplateView
from banner.models import Banner
from news.models import  News
from tournaments.models import Tournament, Team
from links.models import YoutubeLink, SocialNetworkLink, MapsLink
from calendar_matches.models import Match

class MainView(TemplateView):
    template_name = "main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_qs'] = News.objects.filter(published=True).order_by('-date_pub')[:6]
        current_tournament = Tournament.objects.filter(on_main=True).first()
        if current_tournament:
            context['current_tournament'] = current_tournament
            is_position_teams = current_tournament.team.filter(is_active=True).exclude(position_number=None).order_by('position_number')
            zero_position_teams = current_tournament.team.filter(is_active=True, position_number=None)
            context['teams'] = list(chain(is_position_teams, zero_position_teams))

        youtube_link = YoutubeLink.objects.filter(on_main=True).first()
        if youtube_link:
            context['youtube_link'] = youtube_link
        youtube_blog = YoutubeLink.objects.exclude(id=youtube_link.id).order_by('-id')[:6]
        if youtube_blog:
            context['youtube_blog'] = youtube_blog
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
        maps_link = MapsLink.objects.filter(is_active=True).first()
        if maps_link:
            context['maps_link'] = maps_link.iframe

        fcke_team = Team.objects.filter(is_fcke=True).first()
        home_matches = Match.objects.filter(tournament=current_tournament, home_team=fcke_team).exclude(start_time=None)
        guest_matches = Match.objects.filter(tournament=current_tournament, guest_team=fcke_team).exclude(start_time=None)
        context['home_matches'] = home_matches
        context['guest_matches'] = guest_matches
        fcke_matches_list = sorted(chain(home_matches, guest_matches), key=lambda instance: instance.start_time)
        context['fcke_matches_list'] = fcke_matches_list
        banner = Banner.objects.filter(published=True).order_by('-id').first()
        context['banner'] = banner if banner else None
        return context
