"""Register the User model with the Django admin site."""

from django.contrib import admin

# Register your models here.
from .models import User

admin.site.register(User)
