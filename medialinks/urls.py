from django.urls import path

from . import views

app_name = 'medialinks'
urlpatterns = [
    path('article_list/', views.ArticlesListView.as_view(), name='articles_list'),
    # path('article_detail/<slug:slug>/', views.ArticleDetailView.as_view(), name='news_detail'),
]
