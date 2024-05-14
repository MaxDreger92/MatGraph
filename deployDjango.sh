#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Navigate to frontend directory
cd frontend/

# Remove existing build directory
sudo rm -rf build/

# Build the frontend application
npm run build

# Navigate back to the root directory of your Django project
cd ..

# Remove existing static files directory
sudo rm -rf mat2devplatform/static/

# Collect static files
python manage.py collectstatic --no-input

# Move collected static files
sudo mv mat2devplatform/static/static/* mat2devplatform/static/

# Remove redundant static directory
sudo rm -rf mat2devplatform/static/static/

# Restart Gunicorn service
sudo systemctl restart gunicorn
