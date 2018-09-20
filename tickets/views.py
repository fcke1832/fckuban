from django.views.generic.base import TemplateView


class TicketSaleView(TemplateView):
    template_name = 'ticket_sale.html'
