"""Defines the URL patterns for the tasks app."""

from django.urls import path

from .views import StudyLogAPIView, TaskAPIView, TaskVerifyPaymentAndUpdateStatusAPIView

app_name = "tasks"

urlpatterns = [
    path("", TaskAPIView.as_view(), name="task"),
    path(
        "<uuid:task_id>/verify-and-start/",
        TaskVerifyPaymentAndUpdateStatusAPIView.as_view(),
        name="task-verify-and-start",
    ),
    path("<uuid:task_id>/logs/", StudyLogAPIView.as_view(), name="study-log"),
]
