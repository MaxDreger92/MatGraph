FROM node:20-bullseye
WORKDIR /app/userBackendNodeJS
COPY userBackendNodeJS/ ./
RUN npm install
RUN npm run build
EXPOSE 3000
CMD ["node", "build/server.js"]
