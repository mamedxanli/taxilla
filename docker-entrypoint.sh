#!/bin/bash
set -e
cd /src
# Collect static files
# echo "Collect static files"
# python manage.py collectstatic --noinput

# Build docs
echo "Generating documentation ..."
make -C docs html

# Apply database migrations
echo "Applying database migrations ..."
python manage.py migrate

# Create an initial admin user
echo "Creating default 'admin' user with password 'admin' ..."
python manage.py loaddata docker-django-users.json

# Start Celery
echo "Starting Celery in multi mode ..."
celery multi start worker -A taxilla

# Start server
echo "Starting Django server ..."
python manage.py runserver 0.0.0.0:8099
