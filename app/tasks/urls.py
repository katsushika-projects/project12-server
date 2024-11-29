"""Defines the URL patterns for the tasks app."""

from django.urls import path

from .views import StudyLogAPIView, TaskAPIView

app_name = "tasks"

urlpatterns = [
    path("", TaskAPIView.as_view(), name="task"),
    path("<uuid:task_id>/logs/", StudyLogAPIView.as_view(), name="study-log"),
]
