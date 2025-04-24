"""payments app config."""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """Payments app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
