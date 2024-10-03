FROM nikolaik/python-nodejs:python3.10-nodejs20

WORKDIR /app/userBackendNodeJS

COPY userBackendNodeJS/ /app

RUN apt-get update && \
    npm install && \
    npm install -g pm2

EXPOSE 8080

ENTRYPOINT ["/app/deployUserBackend_docker.sh"]