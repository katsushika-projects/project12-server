# Generated by Django 4.2.16 on 2024-11-29 13:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid6


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.UUIDField(default=uuid6.uuid7, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('fine', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('N', 'Not Started'), ('I', 'In Progress'), ('D', 'Done'), ('F', 'Failed')], default='N', max_length=1)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('due_time', models.DateTimeField(blank=True, null=True)),
                ('target_minutes', models.PositiveIntegerField()),
                ('achieved_minutes', models.PositiveIntegerField(default=0)),
                ('requires_new_task_creation', models.BooleanField(default=True)),
                ('new_task_created', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudyLog',
            fields=[
                ('id', models.UUIDField(default=uuid6.uuid7, editable=False, primary_key=True, serialize=False)),
                ('minutes', models.PositiveIntegerField()),
                ('is_studying', models.BooleanField(default=False)),
                ('comment', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
