#!/bin/bash
set -e
echo "✅ Entrypoint script is running..."

rm -rf mat2devplatform/static/

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py setup_neo4j

echo "🚀 Starting Gunicorn on port ${DJANGO_PORT:-8000}..."
exec gunicorn --workers=3 mat2devplatform.wsgi:application --bind 0.0.0.0:${DJANGO_PORT:-8000}
