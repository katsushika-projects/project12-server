"""Define the views for the users app."""

from typing import ClassVar

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class UserAPIView(APIView):
    """Define the UserAPIView class."""

    permission_classes: ClassVar = [IsAuthenticated]

    def delete(self, request: Request) -> Response:
        """Delete the user."""
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
