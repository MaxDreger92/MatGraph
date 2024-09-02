const { execSync } = require('child_process');
const packageJson = require('./package.json');

process.env.REACT_APP_VERSION = packageJson.version;
execSync('react-scripts build', { stdio: 'inherit' });