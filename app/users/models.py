"""Define the custom User model."""

import uuid6
from django.contrib.auth.models import AbstractUser
from django.db import models

from tasks.models import Task


class User(AbstractUser):
    """Define the custom User model."""

    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    # 他のフィールドはAbstractUserが継承しているのでそのまま使用可能

    def total_achieved_minutes(self) -> int:
        """Calculate the total achieved minutes for the user."""
        # ここに実装を追加
        tasks = Task.objects.filter(user=self)
        return sum(task.achieved_minutes for task in tasks)

    def total_challenge_amount(self) -> int:
        """Calculate the total challenge amount for the user."""
        tasks = Task.objects.filter(user=self).exclude(status=Task.NOT_STARTED)
        return sum(task.fine for task in tasks)

    def total_loss_amount(self) -> int:
        """Calculate the total loss amount for the user."""
        tasks = Task.objects.filter(user=self, status=Task.FAILED)
        return sum(task.fine for task in tasks)
