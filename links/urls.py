from django.urls import path

from . import views

app_name = "video"
urlpatterns = [
    path("", views.VKVideoListView.as_view(), name="video_list"),
]
