"""URL configuration for the payments app in a Django project."""

from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("mock_stripe_success_redirect/", views.mock_stripe_success_redirect, name="mock_stripe_success_redirect"),
]
