#!/bin/bash

rm -rf mat2devplatform/static/

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate

gunicorn --workers=3 mat2devplatform.wsgi:application --bind 0.0.0.0:$DJANGO_PORT
