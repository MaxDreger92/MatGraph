const dotenv = require('dotenv');

dotenv.config();  // This will load the .env file variables into process.env

module.exports = {
  apps: [{
    name: 'matGraph-userBackend',
    script: 'build/server.js',
    env: {
      ...process.env,  // Spread operator to include all loaded environment variables
    }
  }]
}
