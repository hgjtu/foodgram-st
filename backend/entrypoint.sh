#!/bin/bash

echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

python manage.py migrate

python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
END

python manage.py load_ingredients /app/data/ingredients.json

python manage.py collectstatic --noinput

# cp -r /app/media_ex/. /app/media/

exec gunicorn --bind 0.0.0.0:8000 foodgramApi.wsgi:application 