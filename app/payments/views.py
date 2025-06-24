"""Mock Stripe success redirect view."""

from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect


def mock_stripe_success_redirect(request: HttpRequest) -> HttpResponseRedirect:
    """Mock Stripe success redirect view."""
    task_id = request.GET.get("task_id")
    client_domain = settings.CLIENT_DOMAIN
    return redirect(f"{client_domain}/dashboard?taskId={task_id}&payment=success")
