FROM python:3.10-bullseye AS intermediate

WORKDIR /app

RUN python3 -m pip install --upgrade pip setuptools

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install gunicorn

COPY . /app

RUN mkdir -p /app/static

RUN python3 manage.py collectstatic --noinput

RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY deployDjango_docker.sh /app/deployDjango_docker.sh
RUN chmod +x /app/deployDjango_docker.sh

ENTRYPOINT ["/app/deployDjango_docker.sh"]
