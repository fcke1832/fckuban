from django.views.generic import ListView
from links.models import SocialNetworkLink
from fckuban.views import get_calendar, get_calendar_matches
from birthdays.views import today_birtdays, check_today
from .models import Partner


class PartnerListView(ListView):
    model = Partner
    template_name = 'partners_list.html'

    def get_context_data(self, **kwargs):
        context = super(PartnerListView, self).get_context_data(**kwargs)
        context['partners'] = Partner.objects.filter(type_partner=self.model.PARTNER, is_active=True)
        context['sponsors'] = Partner.objects.filter(type_partner=self.model.SPONSOR, is_active=True)

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
