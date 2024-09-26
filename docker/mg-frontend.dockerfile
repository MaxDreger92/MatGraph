FROM python:3.10-bullseye AS intermediate

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y curl gnupg python3-venv && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

RUN python3 -m pip install --upgrade pip setuptools

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install gunicorn

RUN chmod +x /app/deployDjango_docker.sh

RUN python3 manage.py collectstatic --noinput

ENTRYPOINT ["/app/deployDjango_docker.sh"]
