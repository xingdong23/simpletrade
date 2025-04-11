# SimpleTrade 项目结构

本文档描述了SimpleTrade项目的目录结构和各个组件的功能。

## 顶级目录

```
simpletrade/
├── docs/                  # 项目文档
├── simpletrade/           # 主要代码包
├── tests/                 # 测试代码
├── examples/              # 示例代码
├── vnpy/                  # vnpy子模块
├── setup.py               # 包安装配置
└── README.md              # 项目说明
```

## 主要代码包 (simpletrade/)

```
simpletrade/
├── api/                   # API接口
│   ├── data.py            # 数据管理API
│   ├── analysis.py        # 数据分析API
│   ├── server.py          # API服务器
│   └── wechat/            # 微信小程序API
├── core/                  # 核心功能
│   ├── data/              # 数据管理
│   ├── message/           # 消息处理
│   └── analysis/          # 数据分析
└── apps/                  # 应用模块
    └── st_datamanager/    # 数据管理应用
```

## 测试代码 (tests/)

```
tests/
├── unit/                  # 单元测试
├── integration/           # 集成测试
├── scripts/               # 测试脚本
└── conftest.py            # 测试配置
```

## 示例代码 (examples/)

```
examples/
├── data_management_example.py  # 数据管理示例
└── api_example.py              # API服务示例
```

## 文档 (docs/)

```
docs/
├── project_structure.md        # 项目结构文档
├── installation.md             # 安装指南
└── api_reference.md            # API参考
```

## vnpy子模块 (vnpy/)

vnpy是一个开源的Python交易平台，我们将其作为子模块集成到项目中。我们直接使用vnpy的数据模型和数据管理功能，而不是重新实现这些功能。
