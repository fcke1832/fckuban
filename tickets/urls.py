from django.urls import path

from . import views

app_name = 'tickets'
urlpatterns = [
    path('sale', views.TicketSaleView.as_view(), name='ticket_sale'),
]