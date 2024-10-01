#!/bin/bash

cd frontend/

rm -rf build/

npm run build

cd ..

rm -rf mat2devplatform/static/

python manage.py collectstatic --no-input

mv mat2devplatform/static/static/* mat2devplatform/static/

rm -rf mat2devplatform/static/static/

gunicorn --workers=3 mat2devplatform.wsgi:application --bind 0.0.0.0:8000
