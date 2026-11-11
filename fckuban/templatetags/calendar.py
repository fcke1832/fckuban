from django import template
from django.db.models import Prefetch

from calendar_matches.models import Match
from tournaments.models import Tournament

register = template.Library()


def get_calendar():
    """
    Получаем турниры для календаря и связанные с ними матчи
    """
    return Tournament.objects.filter(in_calendar=True).prefetch_related(
        Prefetch("match", queryset=Match.objects.filter(is_active=True))
    )


def get_tournament():
    try:
        return Tournament.objects.filter(on_main=True)[0]
    except:
        return None


@register.simple_tag(takes_context=True)
def current_tournament(context):
    current_tournament = get_tournament()
    if current_tournament:
        is_position_teams = (
            current_tournament.team.filter(is_active=True).exclude(position_number=None).order_by("position_number")
        )
        zero_position_teams = current_tournament.team.filter(is_active=True, position_number=None)
        # list(chain(is_position_teams, zero_position_teams)) = context['teams']
    return current_tournament


@register.simple_tag(takes_context=True)
def calendar_tournaments(context):
    calendar_tournaments = get_calendar()
    # calendar_tournaments = context['calendar_tournaments']
    return calendar_tournaments


# from django.views.generic import TemplateView

# from fckuban.utils import check_now
# from banner.models import Banner
# from news.models import News
# from links.models import YoutubeLink, SocialNetworkLink, MapsLink, Hashtag
# from calendar_matches.models import Match
# from seo.models import SeoData
# from birthdays.views import today_birtdays, check_today


# def get_calendar_matches(calendar_tournaments):
#     now = check_now().date()
#     calendar_matches = []
#     futured_calendar_matches = []
#     for tournament in calendar_tournaments:
#         for match in tournament.match.all().order_by('-start_time'):
#             if match not in calendar_matches:
#                 calendar_matches.append(match)
#                 if match.start_time.date() >= now:
#                     futured_calendar_matches.append(match)
#     return calendar_matches, futured_calendar_matches


#     def check_news_time(self, news):
#         """
#         Принимает кверисет news с отложенными по публикации новостями
#         Если время публикации настало - переводим новость в публикуемые
#         """
#         now = check_now()
#         for news_item in news:
#             if news_item.date_pub < now:
#                 news_item.published = True
#                 news_item.is_periodic = False
#                 news_item.save()

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         periodic_news = self._get_periodic_news()

#         if periodic_news:
#             self.check_news_time(periodic_news)
#         context['news_qs'] = self._get_news()

#         current_tournament = get_tournament()
#         calendar_tournaments = get_calendar()

#         if current_tournament:
#             context['current_tournament'] = current_tournament
#             is_position_teams = current_tournament.team.filter(is_active=True).exclude(position_number=None).order_by('position_number')
#             zero_position_teams = current_tournament.team.filter(is_active=True, position_number=None)
#             context['teams'] = list(chain(is_position_teams, zero_position_teams))

#         try:
#             youtube_link = YoutubeLink.objects.filter(on_main=True)[0]
#         except:
#             youtube_link = None
#         if youtube_link:
#             context['youtube_link'] = youtube_link


#         try:
#             fcke_team = Team.objects.filter(is_fcke=True)[0]
#         except:
#             fcke_team = None

#         context['calendar_tournaments'] = calendar_tournaments
#         calendar_matches, futured_calendar_matches = get_calendar_matches(calendar_tournaments)
#         context['calendar_matches'] = sorted(calendar_matches, key=lambda instance: instance.start_time)
#         try:
#             context['future_match'] = (sorted(futured_calendar_matches, key=lambda instance: instance.start_time))[0]
#         except IndexError:
#             context['future_match'] = context['calendar_matches'][-1]
#         context['birthdays'] = today_birtdays()
#         context['today_date'] = check_today()
