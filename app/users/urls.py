"""Defines the URL patterns for the users app."""

from django.urls import path

from .views import UserAPIView

urlpatterns = [path("", UserAPIView.as_view(), name="")]
