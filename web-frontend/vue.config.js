const path = require('path');
const webpack = require('webpack');

module.exports = {
  lintOnSave: false,
  transpileDependencies: [
    // 'quasar' // 告诉 Babel 转译 Quasar 依赖 - Temporarily remove for Quasar v1
  ],
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    public: 'http://localhost:8080',
    sockHost: 'localhost',
    sockPort: 8080,
    // 代理 API 请求到后端服务器
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8003', // 使用 IP 地址而不是主机名
        changeOrigin: true,
        logLevel: 'debug' // 打印调试日志
      }
    }
  },
  configureWebpack: {
    resolve: {
      alias: {
        // 为 webpack 4 提供兼容性解决方案
        'webpack/buildin/global.js': path.resolve(__dirname, 'src/polyfills/global.js')
      }
    },
    plugins: [
      // 添加全局变量
      new webpack.ProvidePlugin({
        global: path.resolve(__dirname, 'src/polyfills/global.js')
      })
    ]
  }
}
