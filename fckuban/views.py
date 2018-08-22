from django.views.generic import ListView, View, TemplateView


class MainView(TemplateView):
    template_name = "main.html"