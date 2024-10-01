#!/bin/bash

cd userBackendNodeJS/

rm -rf build/

npm run build

node build/server.js
