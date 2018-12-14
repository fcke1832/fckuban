from itertools import chain

from django.db.models import Prefetch
from django.views.generic import TemplateView
from django.utils import timezone

from banner.models import Banner
from news.models import News
from tournaments.models import Tournament, Team
from links.models import YoutubeLink, SocialNetworkLink, MapsLink, Hashtag
from calendar_matches.models import Match
from seo.models import SeoData


class MainView(TemplateView):
    template_name = "main.html"

    def _seo_data(self):
        seo_data = SeoData.objects.last()
        return seo_data

    def _get_news(self):
        return News.objects.filter(published=True).order_by('-date_pub')[:5]

    def _get_tournament(self):
        try:
            return Tournament.objects.filter(on_main=True)[0]
        except:
            return None

    def _get_periodic_news(self):
        return News.objects.filter(published=False, is_periodic=True)

    def _get_calendar(self):
        """
        Получаем турниры для календаря и связанные с ними матчи
        """
        return Tournament.objects.filter(in_calendar=True).prefetch_related(
            Prefetch('match', queryset=Match.objects.filter(is_active=True))
        )

    def check_news_time(self, news):
        """
        Принимает кверисет news с отложенными по публикации новостями
        Если время публикации настало - переводим новость в публикуемые
        """
        now = timezone.now()
        for news_item in news:
            if news_item.date_pub < now:
                news_item.published = True
                news_item.is_periodic = False
                news_item.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodic_news = self._get_periodic_news()

        if periodic_news:
            self.check_news_time(periodic_news)
        context['news_qs'] = self._get_news()
        current_tournament = self._get_tournament()
        calendar_tournaments = self._get_calendar()

        if current_tournament:
            context['current_tournament'] = current_tournament
            is_position_teams = current_tournament.team.filter(is_active=True).exclude(position_number=None).order_by('position_number')
            zero_position_teams = current_tournament.team.filter(is_active=True, position_number=None)
            context['teams'] = list(chain(is_position_teams, zero_position_teams))

        try:
            youtube_link = YoutubeLink.objects.filter(on_main=True)[0]
        except:
            youtube_link = None
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
                elif 'https://twitter.com/' in link.link:
                    context['twitter_link'] = link.link
        try:
            maps_link = MapsLink.objects.filter(is_active=True)[0]
        except:
            maps_link = None
        if maps_link:
            context['maps_link'] = maps_link.iframe

        try:
            fcke_team = Team.objects.filter(is_fcke=True)[0]
        except:
            fcke_team = None

        # home_matches = Match.objects.filter(tournament=current_tournament, home_team=fcke_team).exclude(start_time=None)
        # guest_matches = Match.objects.filter(tournament=current_tournament, guest_team=fcke_team).exclude(start_time=None)
        # context['home_matches'] = home_matches
        # context['guest_matches'] = guest_matches
        context['calendar_tournaments'] = calendar_tournaments
        calendar_matches = []
        for tournament in calendar_tournaments:
            for match in tournament.match.all().order_by('-start_time'):
                if match not in calendar_matches:
                    calendar_matches.append(match)
        context['calendar_matches'] = sorted(calendar_matches, key=lambda instance: instance.start_time)

        # fcke_matches_list = sorted(chain(home_matches, guest_matches), key=lambda instance: instance.start_time)
        # context['fcke_matches_list'] = fcke_matches_list

        try:
            banner = Banner.objects.filter(published=True).order_by('-id')[0]
        except:
            banner = None

        try:
            hashtag = Hashtag.objects.filter(is_active=True).order_by('-id')[0]
        except:
            hashtag = None
        context['banner'] = banner
        context['hashtag'] = hashtag
        context['seo'] = self._seo_data()
        return context
