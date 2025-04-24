"""Define the serializers for the tasks app."""

from typing import ClassVar

from django.conf import settings
from rest_framework import serializers

from .models import StudyLog, Task


class TaskSerializer(serializers.ModelSerializer):
    """Define the TaskSerializer class."""

    class Meta:
        """Define the TaskSerializer class."""

        model = Task
        fields = "__all__"


class TaskCreateSerializer(serializers.ModelSerializer):
    """Define the TaskCreateSerializer class."""

    class Meta:
        """Define the TaskCreateSerializer class."""

        model = Task
        fields = "__all__"
        read_only_fields: ClassVar = ["user", "status", "start_time", "due_time", "achieved_minutes"]

    def create(self, validated_data: dict) -> Task:
        """Handle fine-specific logic when creating a new task."""
        if 0 < validated_data.get("fine") < int(settings.STRIPE_MINIMUM_AMOUNT):
            message = {"fine": ["罰金額は、「0円」または「50円以上」である必要があります。"]}
            raise serializers.ValidationError(message)
        return super().create(validated_data)


class StudyLogSerializer(serializers.ModelSerializer):
    """Define the StudyLogSerializer class."""

    class Meta:
        """Define the StudyLogSerializer class."""

        model = StudyLog
        fields = "__all__"
