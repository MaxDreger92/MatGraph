#!/bin/bash
set -e
echo "✅ Entrypoint script is running..."

# Wait for Postgres to be ready
echo "⏳ Waiting for Postgres to be ready..."
until pg_isready -h mg-postgres -p 5432 -U $POSTGRES_USER; do
  sleep 1
done
echo "✅ Postgres is ready."

rm -rf mat2devplatform/static/

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py setup_neo4j

echo "🚀 Starting Gunicorn on port ${DJANGO_PORT:-8000}..."
exec gunicorn --workers=3 mat2devplatform.wsgi:application --bind 0.0.0.0:${DJANGO_PORT:-8000}
