from django.urls import path

from . import views

app_name = 'news'
urlpatterns = [
    path('newslist/', views.NewsListView.as_view(), name='news_list'),
    path('news_detail/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('newslist_preview/', views.news_list_preview, name='news_list_preview'),
]