from django.urls import path

from . import views

app_name = 'team'
urlpatterns = [
    path('all_team/', views.TeamView.as_view(), name='all_team'),
]