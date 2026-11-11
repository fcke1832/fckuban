from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import render
from django.views.generic import TemplateView

from banner.models import Banner
from calendar_matches.models import Match
from fckuban import seo as seo_helpers
from fckuban.context import calendar_context, social_links_context
from fckuban.utils import check_now
from fckuban.versioning import VersionedTemplateMixin
from links.models import Hashtag, MapsLink, YoutubeLink
from news.models import News
from partners.models import Partner
from seo.models import SeoData
from tournaments.models import Tournament


def robots_txt(request):
    """Отдаёт robots.txt с абсолютной ссылкой на карту сайта."""
    return render(request, "robots.txt", content_type="text/plain")


def get_hashtag():
    try:
        hashtag = Hashtag.objects.filter(is_active=True).order_by("-id")[0]
    except:
        hashtag = None
    return hashtag


def seo_data():
    seo_data = SeoData.objects.last()
    return seo_data


def get_tournament():
    try:
        return Tournament.objects.filter(on_main=True)[0]
    except:
        return None


def get_calendar_matches(calendar_tournaments):
    now = check_now().date()
    calendar_matches = []
    futured_calendar_matches = []
    for tournament in calendar_tournaments:
        # Порядок матчей задают вызывающие функции; здесь важен только
        # prefetch из get_calendar(), иначе на каждый турнир будет запрос.
        for match in tournament.match.all():
            if match not in calendar_matches:
                calendar_matches.append(match)
                if match.start_time.date() >= now:
                    futured_calendar_matches.append(match)
    return calendar_matches, futured_calendar_matches


def get_calendar():
    """
    Получаем турниры для календаря и связанные с ними матчи
    """
    return Tournament.objects.filter(in_calendar=True).prefetch_related(
        Prefetch(
            "match",
            queryset=Match.objects.filter(is_active=True).select_related(
                "home_team",
                "guest_team",
                "tournament",
            ),
        )
    )


class MainView(VersionedTemplateMixin, TemplateView):
    template_name = "main.html"

    def _get_news(self):
        return News.objects.filter(published=True).prefetch_related("hashtags").order_by("-date_pub")[:5]

    def _get_periodic_news(self):
        return News.objects.filter(published=False, is_periodic=True)

    def _get_banner(self):
        # TODO - оптимизировать
        try:
            banner = Banner.objects.filter(published=True).order_by("-id")[0]
        except:
            banner = None
        return banner

    def check_news_time(self, news):
        """
        Принимает кверисет news с отложенными по публикации новостями
        Если время публикации настало - переводим новость в публикуемые
        """
        # TODO - оптимизировать
        now = check_now()
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
        context["news_qs"] = self._get_news()
        # preload LCP-картинки главной нужен только v2; в v1 не тратим генерацию.
        hero_image = ""
        if getattr(settings, "SITE_VERSION", "v1") == "v2" and context["news_qs"]:
            hero_image = context["news_qs"][0].get_thumbnail_center
        context["hero_image"] = hero_image or ""
        context["partners"] = Partner.objects.filter(is_active=True).order_by("-number", "title")[:8]

        current_tournament = get_tournament()
        calendar_tournaments = get_calendar()

        if current_tournament:
            context["current_tournament"] = current_tournament
            active_teams = list(current_tournament.team.filter(is_active=True))
            positioned = sorted(
                (team for team in active_teams if team.position_number is not None),
                key=lambda team: team.position_number,
            )
            context["teams"] = positioned + [team for team in active_teams if team.position_number is None]

        try:
            youtube_link = YoutubeLink.objects.filter(on_main=True)[0]
        except:
            youtube_link = None
        if youtube_link:
            context["youtube_link"] = youtube_link

        try:
            youtube_blog = YoutubeLink.objects.exclude(id=youtube_link.id).order_by("-id")[:6]
        except AttributeError:
            youtube_blog = None
        if youtube_blog:
            context["youtube_blog"] = youtube_blog

        context.update(social_links_context())

        try:
            maps_link = MapsLink.objects.filter(is_active=True)[0]
        except:
            maps_link = None
        if maps_link:
            context["maps_link"] = maps_link.iframe
            context["maps_title"] = maps_link.title

        context["calendar_tournaments"] = calendar_tournaments
        context.update(calendar_context(calendar_tournaments))
        now = check_now()
        context["upcoming_matches"] = [
            match for match in context["calendar_matches"] if match.start_time and match.start_time >= now
        ][:3]
        context["banner"] = self._get_banner()
        context["hashtag"] = get_hashtag()
        context["seo"] = seo_data()
        seo_obj = context["seo"]
        context["page_description"] = seo_helpers.make_description(
            getattr(seo_obj, "description", "") if seo_obj else "",
        )
        context["jsonld"] = seo_helpers.graph(
            seo_helpers.organization_node(self.request),
            seo_helpers.website_node(self.request),
            seo_helpers.sports_event_node(context.get("future_match"), self.request),
        )

        return context
