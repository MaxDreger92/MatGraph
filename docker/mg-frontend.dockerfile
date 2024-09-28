FROM nikolaik/python-nodejs:python3.10-nodejs20

WORKDIR /app

# Copy application files
COPY . /app

# Install system dependencies (if any)
RUN apt-get update && \
    apt-get install -y python3-venv

# Upgrade pip and setuptools
RUN python3 -m pip install --upgrade pip setuptools

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
RUN npm run build
EXPOSE 3000


WORKDIR /app

# Install gunicorn
RUN python3 -m pip install gunicorn

# Make your deploy script executable
RUN chmod +x /app/deployDjango_docker.sh

# Collect static files
RUN python3 manage.py collectstatic --noinput

# Expose necessary ports (if needed)
EXPOSE 8000

# Run the application
ENTRYPOINT ["/app/deployDjango_docker.sh"]

