"""fckuban URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from dues.admin import dues_admin_site

from . import views
from .sitemaps import SITEMAPS

urlpatterns = [
    path("", views.MainView.as_view(), name="index"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("admin/", admin.site.urls),
    path("kroo/manage/", dues_admin_site.urls),
    path("kroo/", include("kroo.urls", namespace="kroo")),
    path("news/", include("news.urls", namespace="news")),
    path("media/", include("medialinks.urls", namespace="medialinks")),
    path("tickets/", include("tickets.urls", namespace="tickets")),
    path("team/", include("team.urls", namespace="team")),
    path("partners/", include("partners.urls", namespace="partners")),
    path("tournaments/", include("tournaments.urls", namespace="tournaments")),
    path("video/", include("links.urls", namespace="video")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
