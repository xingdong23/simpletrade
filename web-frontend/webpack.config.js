const path = require('path');
const webpack = require('webpack');

module.exports = {
  resolve: {
    fallback: {
      global: path.resolve(__dirname, 'src/polyfills/global.js')
    }
  },
  plugins: [
    // 添加全局变量
    new webpack.ProvidePlugin({
      global: path.resolve(__dirname, 'src/polyfills/global.js')
    })
  ]
};
