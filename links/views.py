from django.views.generic import ListView

from fckuban import seo
from fckuban.context import shell_context

from .models import VKVideo

VIDEOS_PER_PAGE = 9


class VKVideoListView(ListView):
    """Страница «Видео»: ролики VK Видео с главным роликом и пагинацией."""

    model = VKVideo
    template_name = "v2/video_list.html"
    context_object_name = "videos"
    paginate_by = VIDEOS_PER_PAGE

    def get_queryset(self):
        return VKVideo.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context.get("page_obj")
        featured_video = None
        if page_obj is None or page_obj.number == 1:
            featured_video = self.get_queryset().filter(on_main=True).first()
        context["featured_video"] = featured_video
        if featured_video:
            context["videos"] = [video for video in context["videos"] if video.pk != featured_video.pk]
        context.update(shell_context())
        context["page_title"] = "Видео"
        context["page_description"] = seo.make_description(
            "Видео футбольного клуба «Кубань»: матчи, интервью и события клуба."
        )
        video_nodes = []
        if featured_video:
            video_nodes.append(seo.video_object_node(featured_video, self.request))
        video_nodes.extend(
            seo.video_object_node(video, self.request) for video in list(context.get("videos") or [])[:10]
        )
        context["jsonld"] = seo.graph(
            seo.organization_node(self.request),
            *video_nodes,
            seo.breadcrumbs_node(
                self.request,
                [("Главная", "/"), ("Видео", "/video/")],
            ),
        )
        return context
