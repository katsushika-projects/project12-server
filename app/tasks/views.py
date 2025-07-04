"""Define the Task views."""

import base64
from typing import ClassVar

from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from config.exceptions import CreateCheckoutSessionError
from payments.utils import create_checkout_session
from users.models import User

from .models import StudyLog, Task
from .serializers import StudyLogSerializer, TaskCreateSerializer, TaskSerializer
from .utils import get_ai_response


class TaskAPIView(APIView):
    """Define the TaskAPIView class."""

    permission_classes: ClassVar = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return a list of tasks."""
        tasks = Task.objects.filter(user=request.user, status__in=[Task.IN_PROGRESS, Task.DONE, Task.FAILED])
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a new task."""
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            # 新しいタスクが作成されたことによる過去タスクのステータス更新
            serializer.instance.update_new_task_created()

            if settings.USE_STRIPE:
                # StripeのCheckoutセッションを作成
                try:
                    payment_url = create_checkout_session(
                        description="支払いから5日以内にタスクを達成しましょう!",
                        name=str(serializer.instance.name),
                        task_id=str(serializer.instance.id),
                        unit_amount=int(serializer.instance.fine),
                        email=str(request.user.email),
                    )
                except CreateCheckoutSessionError as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                payment_url = request.build_absolute_uri(
                    reverse("payments:mock_stripe_success_redirect") + f"?task_id={serializer.instance.id}"
                )

            data = {
                "payment_url": payment_url,  # Stripeの決済URLをここに設定
                "task": serializer.data,
            }

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailAPIView(APIView):
    """Define the TaskDetailAPIView class."""

    permission_classes: ClassVar = [IsAuthenticated]

    def get(self, request: Request, task_id: str) -> Response:
        """Return a task detail."""
        task = Task.objects.get(id=task_id)
        if not task:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        if task.user != request.user:
            return Response({"error": "Task is not owned by the user"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskSerializer(task)
        return Response(serializer.data)


class TaskVerifyPaymentAndUpdateStatusAPIView(APIView):
    """Define the TaskVerifyPaymentAndUpdateStatusAPIView class."""

    permission_classes: ClassVar = [IsAuthenticated]

    def post(self, request: Request, task_id: str) -> Response:
        """Verify a task."""
        task = Task.objects.get(id=task_id)
        if not task:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        if task.user != request.user:
            return Response({"error": "Task is not owned by the user"}, status=status.HTTP_403_FORBIDDEN)

        task.verify_payment_and_update_status()

        serializer = TaskSerializer(task)
        return Response(serializer.data)


class StudyLogAPIView(APIView):
    """Define the StudyLogAPIView class."""

    permission_classes: ClassVar = [IsAuthenticated]

    def get(self, request: Request, task_id: str) -> Response:
        """Return a list of study logs for the task."""
        task = Task.objects.get(id=task_id)
        if not task:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        if task.user != request.user:
            return Response({"error": "Task is not owned by the user"}, status=status.HTTP_403_FORBIDDEN)

        # 五個だけ取得
        study_logs = StudyLog.objects.filter(user=request.user, task=task).order_by("-created_at")[:5]
        serializer = StudyLogSerializer(study_logs, many=True)
        return Response(serializer.data)

    def post(self, request: Request, task_id: str) -> Response:
        """Create a new study log."""
        # Validate task existence and ownership
        task = self.validate_task(task_id, request.user)
        if isinstance(task, Response):
            return task  # Task validation failed

        # Validate recent study log for the same task
        recent_log_error = self.validate_recent_log(request.user, task)
        if recent_log_error:
            return recent_log_error

        # Validate and parse minutes
        minutes = self.validate_minutes(request.data.get("minutes"))
        if isinstance(minutes, Response):
            return minutes  # Minutes validation failed

        # Validate image and get AI response
        ai_response = self.process_image(request)
        if isinstance(ai_response, Response):
            return ai_response  # Image validation or AI response failed

        # Save the study log
        data = {
            "user": request.user.id,
            "task": task.id,
            "minutes": minutes,
            "is_studying": ai_response["is_studying"],
            "comment": ai_response["comment"],
        }
        serializer = StudyLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            # タスクの達成時間を更新し、完了した場合はステータスを更新
            if data["is_studying"]:
                task.update_progress(minutes)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def validate_task(self, task_id: str, user: User) -> Task | Response:
        """Validate task existence and ownership."""
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        if task.user != user:
            return Response({"error": "Task is not owned by the user"}, status=status.HTTP_403_FORBIDDEN)

        if task.status != Task.IN_PROGRESS:
            return Response({"error": "Task is not in progress"}, status=status.HTTP_400_BAD_REQUEST)

        return task

    def validate_recent_log(self, user: User, task: Task) -> Response | None:
        """Validate if a study log was created recently."""
        latest_study_log = StudyLog.objects.filter(user=user, task=task).order_by("-created_at").first()
        if latest_study_log:
            min_minutes_seconds = settings.STUDY_LOG_MIN_MINUTES * 60
            min_minutes_seconds_minus_thirty_seconds = min_minutes_seconds - 30
            time_diff = (timezone.now() - latest_study_log.created_at).total_seconds()
            if time_diff < min_minutes_seconds_minus_thirty_seconds:
                time_window = min_minutes_seconds_minus_thirty_seconds
                message = f"Study log for the same task has been created within the last {time_window} seconds"
                return Response(
                    {"error": message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return None

    def validate_minutes(self, raw_minutes: str) -> int | Response:
        """Validate the minutes parameter."""
        if not raw_minutes:
            return Response({"error": "Minutes is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            minutes = int(raw_minutes)
        except ValueError:
            return Response({"error": "Minutes must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        min_minutes = settings.STUDY_LOG_MIN_MINUTES
        max_minutes = settings.STUDY_LOG_MAX_MINUTES
        if not min_minutes <= minutes <= max_minutes:
            return Response(
                {"error": f"Minutes must be between {min_minutes} and {max_minutes}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return minutes

    def process_image(self, request: Request) -> dict[str, str | bool]:
        """Validate the image and get AI response."""
        image_file = request.FILES.get("image")
        if not image_file:
            return Response({"error": "Image file is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_content = image_file.read()
            base64_image = base64.b64encode(file_content).decode("utf-8")
        except ValueError:
            return Response({"error": "Invalid image file"}, status=status.HTTP_400_BAD_REQUEST)
        return get_ai_response(base64_image)


class RunTaskCleanupView(APIView):
    """定期実行用."""

    authentication_classes: ClassVar = []  # 必要に応じて設定
    permission_classes: ClassVar = []  # 認証が必要なら設定

    def post(self, _request: Request) -> Response:
        """Run the task cleanup command."""
        call_command("mark_overdue_tasks")
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
