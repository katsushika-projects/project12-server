"""admin."""

from django.contrib import admin

from .models import StudyLog, Task

admin.site.register(Task)
admin.site.register(StudyLog)
