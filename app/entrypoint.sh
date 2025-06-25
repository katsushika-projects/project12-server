#!/bin/sh

# Django のマイグレーションを先に実行
python manage.py migrate --noinput

# python manage.py collectstatic --noinput

# superuser の作成
python manage.py shell << END
from django.contrib.auth import get_user_model
import os
User = get_user_model()
if not User.objects.filter(username=os.environ["DJANGO_SUPERUSER_USERNAME"]).exists():
    User.objects.create_superuser(
        username=os.environ["DJANGO_SUPERUSER_USERNAME"],
        email=os.environ["DJANGO_SUPERUSER_EMAIL"],
        password=os.environ["DJANGO_SUPERUSER_PASSWORD"]
    )
END


# 最後にアプリを起動
exec gunicorn config.wsgi:application -b 0.0.0.0:$PORT
