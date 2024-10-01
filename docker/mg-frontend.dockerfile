FROM nikolaik/python-nodejs:python3.10-nodejs20

WORKDIR /app

COPY . /app

RUN apt-get update

RUN python3 -m pip install --upgrade pip setuptools wheel

RUN python3 -m pip install --no-cache-dir -r requirements.txt

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
RUN npm run build

WORKDIR /app

RUN python3 -m pip install gunicorn

RUN chmod +x /app/deployDjango_docker.sh

RUN python3 manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/app/deployDjango_docker.sh"]

