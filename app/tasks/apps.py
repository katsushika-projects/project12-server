"""Tasks app configuration."""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Tasks app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"
