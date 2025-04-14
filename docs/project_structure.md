# SimpleTrade 项目结构

本文档描述了SimpleTrade项目的目录结构和各个组件的功能。

## 顶级目录

```
simpletrade/
├── ai_context/            # AI协作上下文文档
├── data/                  # 数据文件
├── docs/                  # 项目文档
├── examples/              # 示例代码
├── scripts/               # 脚本文件
├── simpletrade/           # 主要代码包
├── test_data/             # 测试数据
├── tests/                 # 测试代码
├── ui/                    # 旧版UI代码
├── vendors/               # 第三方代码
├── web-frontend/          # Web前端代码
├── setup.py               # 包安装配置
└── README.md              # 项目说明
```

## 主要代码包 (simpletrade/)

```
simpletrade/
├── api/                   # API接口
│   ├── analysis.py        # 数据分析API
│   ├── server.py          # API服务器
│   └── wechat/            # 微信小程序API
├── apps/                  # 应用模块
│   ├── st_datamanager/    # 数据管理应用
│   ├── st_message/        # 消息处理应用
│   └── st_trader/         # 交易应用
├── core/                  # 核心功能
│   ├── analysis/          # 数据分析
│   ├── data/              # 数据管理
│   ├── message/           # 消息处理
│   └── app.py             # 应用基类
├── models/                # 数据模型
└── utils/                 # 工具函数
```

## 脚本文件 (scripts/)

```
scripts/
├── download_tiger_data.py      # 下载老虎数据
├── import_csv_to_database.py   # 导入CSV到数据库
├── import_qlib_to_database.py  # 导入Qlib数据到数据库
├── simple_api_test.py          # API测试
├── start_web_frontend.py       # 启动Web前端
├── subscribe_tiger_data.py      # 订阅老虎数据
└── test_api_server.py           # 测试API服务器
```

## 测试代码 (tests/)

```
tests/
├── integration/           # 集成测试
├── scripts/               # 测试脚本
├── unit/                  # 单元测试
└── conftest.py            # 测试配置
```

## 示例代码 (examples/)

```
examples/
├── api_example.py              # API服务示例
└── data_management_example.py  # 数据管理示例
```

## Web前端代码 (web-frontend/)

```
web-frontend/
├── public/                # 静态资源
├── src/                   # 源代码
│   ├── api/               # API调用
│   ├── components/        # 组件
│   ├── router/            # 路由
│   ├── store/             # 状态管理
│   └── views/             # 视图
│       ├── analysis/       # 分析中心
│       ├── data/           # 数据中心
│       ├── strategy/       # 策略中心
│       └── trading/        # 交易中心
├── package.json           # 包配置
└── vue.config.js          # Vue配置
```

## 第三方代码 (vendors/)

```
vendors/
└── vnpy_tiger/           # 老虎证券网关
```

## AI协作上下文文档 (ai_context/)

```
ai_context/
├── AI_COLLABORATION_GUIDE.md  # AI协作指南
├── CONVERSATION_HISTORY.md    # 对话历史
├── CURRENT_STATUS.md          # 当前状态
└── DECISIONS_LOG.md           # 决策日志
```

## 文档 (docs/)

```
docs/
├── ai_model_guide.md           # AI模型指南
├── api_reference.md            # API参考
├── architecture_diagram.md      # 架构图
├── installation.md             # 安装指南
├── long_term_roadmap.md        # 长期路线图
├── project_structure.md        # 项目结构文档
├── startup_guide.md            # 启动指南
├── technical_specification.md  # 技术规格
└── tiger_gateway_usage.md      # 老虎网关使用指南
```
