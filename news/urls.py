from django.urls import path

from . import views

app_name = 'news'
urlpatterns = [
    path('newslist/', views.NewsListView.as_view(), name='news_list'),
]