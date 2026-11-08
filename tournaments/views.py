from django.views.generic.base import TemplateView
from links.models import SocialNetworkLink
from fckuban.views import get_calendar, get_calendar_matches
from birthdays.views import today_birtdays, check_today
from .models import Tournament


class StandingsView(TemplateView):
    template_name = 'full_standings.html'

    # TODO
    def calculate_statistics(self, tournament, teams):
        for team in teams:
            team.get_tournament_statistics()

    def get_context_data(self, **kwargs):
        context = super(StandingsView, self).get_context_data(**kwargs)
        try:
            current_tournament = Tournament.objects.filter(on_main=True)[0]
            teams = current_tournament.team.filter(is_active=True)
        except IndexError:
            current_tournament = None
            teams = []
        # sorted_teams = self.calculate_statistics(current_tournament, teams)
        context['current_tournament'] = current_tournament
        context['teams'] = teams

        calendar_tournaments = get_calendar()
        calendar_matches, futured_calendar_matches = get_calendar_matches(calendar_tournaments)

        context['calendar_matches'] = sorted(calendar_matches, key=lambda instance: instance.start_time)
        context['birthdays'] = today_birtdays()
        context['today_date'] = check_today()
        try:
            context['future_match'] = (sorted(futured_calendar_matches, key=lambda instance: instance.start_time))[0]
        except IndexError:
            matches = context['calendar_matches']
            context['future_match'] = matches[-1] if matches else None
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
