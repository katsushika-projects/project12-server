"""Defines the URL patterns for the tasks app."""

from django.urls import path

from .views import (
    RunTaskCleanupView,
    StudyLogAPIView,
    TaskAPIView,
    TaskDetailAPIView,
    TaskVerifyPaymentAndUpdateStatusAPIView,
)

app_name = "tasks"

urlpatterns = [
    path("", TaskAPIView.as_view(), name="task"),
    path("<uuid:task_id>/", TaskDetailAPIView.as_view(), name="task-detail"),
    path(
        "<uuid:task_id>/verify-and-start/",
        TaskVerifyPaymentAndUpdateStatusAPIView.as_view(),
        name="task-verify-and-start",
    ),
    path("<uuid:task_id>/logs/", StudyLogAPIView.as_view(), name="study-log"),
    path("run-task-cleanup/", RunTaskCleanupView.as_view(), name="run_task_cleanup"),
]
