"""Define the serializers for the tasks app."""

from typing import ClassVar

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
        if validated_data.get("fine") == 0:
            validated_data["status"] = Task.IN_PROGRESS
        else:
            message = {"fine": ["Fine must be 0 in prototype version."]}
            raise serializers.ValidationError(message)
        return super().create(validated_data)


class StudyLogSerializer(serializers.ModelSerializer):
    """Define the StudyLogSerializer class."""

    class Meta:
        """Define the StudyLogSerializer class."""

        model = StudyLog
        fields = "__all__"
