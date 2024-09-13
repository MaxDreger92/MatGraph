FROM python:3.10-bullseye AS intermediate

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl gnupg python3-venv && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g pm2

RUN python -m venv venv

COPY . /app

RUN chmod +x /app/deployUserBackend_docker.sh

ENTRYPOINT ["/app/deployUserBackend_docker.sh"]