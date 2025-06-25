"""Command to mark overdue tasks as FAILED."""

from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Task


class Command(BaseCommand):
    """Command to mark overdue tasks as FAILED."""

    help = "Mark overdue tasks as FAILED"

    def handle(self, *args, **kwargs) -> None:  # noqa: ARG002, ANN002, ANN003
        """Handle the command to mark overdue tasks as FAILED."""
        now = timezone.now()
        overdue_tasks = Task.objects.filter(status=Task.IN_PROGRESS, due_time__lt=now)

        updated_count = 0
        for task in overdue_tasks:
            task.mark_failed()
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"{updated_count} task(s) marked as FAILED."))
