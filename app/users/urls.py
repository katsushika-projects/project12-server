"""Defines the URL patterns for the users app."""

from django.urls import path

from .views import UserAPIView, UserMyDataAPIView

urlpatterns = [
    path("", UserAPIView.as_view(), name=""),
    path("me/", UserMyDataAPIView.as_view(), name="user-me"),
]
