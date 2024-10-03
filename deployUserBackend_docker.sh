#!/bin/bash

cd userBackendNodeJS/

pm2 stop build/server.js

rm -rf build/

npm run build

pm2 start build/server.js
