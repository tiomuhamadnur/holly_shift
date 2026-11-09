from django.urls import path

from . import settings_views, views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("settings/", settings_views.SystemSettingView.as_view(), name="settings"),
]
