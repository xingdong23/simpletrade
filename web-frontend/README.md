# SimpleTrade Web 前端

这是 SimpleTrade 的 Web 前端项目，使用 Vue.js 开发。

## 功能

- 数据管理：查看、导入、导出和删除交易数据
- 数据分析：计算技术指标和运行策略回测
- 可视化展示：K线图、技术指标图和回测结果

## 技术栈

- Vue.js 2.x
- Element UI
- ECharts
- Axios

## 安装与运行

### 安装依赖

```bash
cd web-frontend
npm install
```

### 开发模式运行

```bash
npm run serve
```

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
web-frontend/
├── public/              # 静态资源
├── src/                 # 源代码
│   ├── api/             # API接口
│   ├── components/      # 组件
│   ├── views/           # 视图
│   ├── App.vue          # 根组件
│   ├── main.js          # 入口文件
│   ├── router/          # 路由配置
│   └── store/           # Vuex状态管理
└── package.json         # 项目配置
```

## 使用说明

1. 确保后端API服务已启动（默认地址：http://localhost:8000）
2. 启动前端开发服务器
3. 在浏览器中访问 http://localhost:8080

## 注意事项

- 本项目需要与SimpleTrade后端API配合使用
- 默认API地址为 http://localhost:8000，如需修改请更新 src/api 目录下的文件
