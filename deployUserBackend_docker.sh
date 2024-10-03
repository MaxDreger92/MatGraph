#!/bin/bash

rm -rf build/

npm run build

node build/server.js
