module.exports = {
  lintOnSave: false,
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    public: 'http://localhost:8080',
    sockHost: 'localhost',
    sockPort: 8080,
    // 可选：如果需要代理 API 请求到后端容器，取消下面的注释并调整
    // proxy: {
    //   '/api': {
    //     target: 'http://api:8003', // 'api' 是后端服务名, 8003 是端口
    //     changeOrigin: true,
    //     // pathRewrite: { '^/api': '/api' } // 如果需要路径重写
    //   }
    // }
  }
}
