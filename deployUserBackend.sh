#!/bin/bash

# Navigate to the userBackendNodeJS directory
cd userBackendNodeJS/

# Stop the PM2-managed process
pm2 stop build/server.js

# Remove existing build directory
sudo rm -rf build/

# Build the Node.js application
npm run build

# Start the PM2-managed process
pm2 start build/server.js
