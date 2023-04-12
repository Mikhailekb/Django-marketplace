from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Представление для отображения главной страницы"""
    template_name = 'pages/main.html'
