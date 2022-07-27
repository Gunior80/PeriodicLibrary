"""PeriodicLibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view()),
    path('<slug:slug>/', views.PeriodicView.as_view(), name="periodical"),
    path('search', views.SearchTags.as_view(), name="search"),
    path('load_url', views.LoadURL.as_view(), name="load_url"),
    path('load_menu', views.LoadMenu.as_view(), name="load_menu"),
    path('viewer/', views.Viewer.as_view(), name="viewer"),
]
