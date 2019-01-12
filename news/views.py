from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse
from links.models import YoutubeLink, SocialNetworkLink
from .models import News, NewsImage


class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'
    context_object_name = 'news_list'

    def get_queryset(self):
        return News.objects.filter(published=True).order_by('-date_pub')


def news_list_preview(request):
    user = request.user
    if not user.is_authenticated and not user.is_superuser and not user.is_staff:
        return redirect(reverse('index'))
    preview_news = News.objects.filter(published=False).order_by('-date_pub')
    template = 'news_list_preview.html'
    return render(request, template, {
        'preview_news': preview_news,
    })


class NewsDetailView(DetailView):
    model = News
    template_name = 'news_detail.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super(NewsDetailView, self).get_context_data(**kwargs)
        context['slider_images'] = NewsImage.objects.filter(image_news=self.object)
        context['another_news'] = News.objects.filter(published=True).exclude(id=self.object.id).order_by('-date_pub')[:4]
        social_networks_links = SocialNetworkLink.objects.all()
        if social_networks_links:
            for link in social_networks_links:
                if 'www.facebook.com/' in link.link:
                    context['facebook_link'] = link.link
                elif 'https://vk.com/' in link.link:
                    context['vk_link'] = link.link
                elif 'www.instagram.com' in link.link:
                    context['instagram_link'] = link.link
                elif 'www.youtube.com' in link.link:
                    context['youtube_channel'] = link.link
                elif 'https://t.me/' in link.link:
                    context['telegram_channel'] = link.link
        return context
