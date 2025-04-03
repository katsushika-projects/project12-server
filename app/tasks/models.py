"""Define the Task model."""

from datetime import timedelta
from typing import ClassVar

import uuid6
from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    """Model representing a task."""

    NOT_STARTED = "N"
    IN_PROGRESS = "I"
    DONE = "D"
    FAILED = "F"

    STATUS_CHOICES: ClassVar = [
        (NOT_STARTED, "Not Started"),
        (IN_PROGRESS, "In Progress"),
        (DONE, "Done"),
        (FAILED, "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    fine = models.PositiveIntegerField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=NOT_STARTED)
    start_time = models.DateTimeField(null=True, blank=True)
    due_time = models.DateTimeField(null=True, blank=True)
    target_minutes = models.PositiveIntegerField()
    achieved_minutes = models.PositiveIntegerField(default=0)
    # 新しいタスクを作成することが、達成条件に含まれるかどうか
    requires_new_task_creation = models.BooleanField(default=True)
    # 新しいタスクが作成されたかどうか
    new_task_created = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Return the title and created_at in a human-readable format."""
        return self.name + " - " + self.created_at.strftime("%Y/%m/%d %H:%M:%S")

    @property
    def can_complete(self) -> bool:
        """Return whether the task can be completed."""
        con1 = self.achieved_minutes >= self.target_minutes
        con2 = not (self.requires_new_task_creation and not self.new_task_created)
        return con1 and con2

    def update_new_task_created(self) -> None:
        """このメソッドを呼んだタスクよりも古いタスクのnew_task_createdをTrueにし, データを更新する."""
        # このメソッドを呼んだタスクよりも古いタスクのnew_task_createdをTrueにする
        Task.objects.filter(
            user=self.user,
            created_at__lt=self.created_at,
            new_task_created=False,
        ).update(new_task_created=True)

        tasks = Task.objects.filter(
            user=self.user,
            created_at__lt=self.created_at,
            status=Task.IN_PROGRESS,
            new_task_created=True,
        )
        # このメソッドを呼んだタスクよりも古いタスクの達成条件を満たすかどうかを確認し更新
        for task in tasks:
            if task.can_complete:
                task.status = Task.DONE
                task.save()

    def update_progress(self, minutes: int) -> None:
        """Update the task progress."""
        self.achieved_minutes += minutes
        self.save()
        if self.can_complete:
            self.status = Task.DONE
        self.save()

    def verify_payment_and_update_status(self) -> None:
        """
        支払い情報が登録されているかを確認し、タスクのステータスを更新します.

        支払い情報が問題ない場合は以下を更新します:
        - start_time
        - due_time
        - status
        """
        if self.status != Task.NOT_STARTED:
            return

        # 罰金額が0の場合
        if self.fine == 0:
            self.status = Task.IN_PROGRESS
            self.start_time = timezone.now()
            self.due_time = self.start_time + timedelta(days=5)
            self.save()
            return
        # 罰金額が0より大きい場合
        # stripe関連
        return


class StudyLog(models.Model):
    """Model representing a study log."""

    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    minutes = models.PositiveIntegerField()
    is_studying = models.BooleanField(default=False)
    comment = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return the title and created_at in a human-readable format."""
        return self.task.name + " - " + self.created_at.strftime("%Y/%m/%d %H:%M:%S")
