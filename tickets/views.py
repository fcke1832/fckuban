from django.views.generic.base import TemplateView
from tickets.models import TicketSaleWidget


class TicketSaleView(TemplateView):
    template_name = 'ticket_sale.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['link_buy_tickets'] = TicketSaleWidget.objects.all()[0].link
        except:
            context['link_buy_tickets'] = None
        return context
