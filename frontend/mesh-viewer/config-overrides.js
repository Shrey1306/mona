const webpack = require('webpack');

module.exports = function override(config) {
  config.resolve.fallback = {
    ...config.resolve.fallback,
    fs: false,  // Ignore 'fs' module
    path: require.resolve('path-browserify'),  // Use 'path-browserify' for 'path'
  };
  return config;
};