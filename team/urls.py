from django.urls import path

from . import views

app_name = 'team'
urlpatterns = [
    path('all_team/', views.TeamView.as_view(), name='all_team'),
    path('all_team/player/<slug:slug>/', views.PLayerView.as_view(), name='player_detail'),
    path('all_team/coach/<slug:slug>/', views.CoachView.as_view(), name='coach_detail'),
]