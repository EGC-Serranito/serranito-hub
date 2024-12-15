const path = require('path');

module.exports = {
  mode: 'development',
  entry: path.resolve(__dirname, './scripts.js'),
  output: {
    filename: 'hubfile.bundle.js',
    path: path.resolve(__dirname, '../../../../static/js'), 
  },
  resolve: {
    fallback: {
      'fs': false
    }
  },
};