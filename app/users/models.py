"""Define the custom User model."""

import uuid6
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Define the custom User model."""

    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    # 他のフィールドはAbstractUserが継承しているのでそのまま使用可能
