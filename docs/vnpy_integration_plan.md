# SimpleTrade vnpy源码集成方案

**版本**: 0.1
**日期**: 2023-10-15
**状态**: 初稿

## 1. 概述

本文档详细描述SimpleTrade项目如何集成vnpy源码，包括目录结构、依赖管理、源码引用和版本控制策略。

## 2. 集成策略

SimpleTrade将采用"源码子模块"的方式集成vnpy，这种方式既保持了对vnpy源码的直接控制，又便于管理和更新。

### 2.1 集成方式比较

| 集成方式 | 优点 | 缺点 | 是否采用 |
|---------|------|------|---------|
| 直接复制源码 | 完全控制源码，修改灵活 | 难以跟踪上游更新，代码冗余 | 否 |
| 作为依赖安装 | 简单，易于更新 | 定制化受限，无法深度修改 | 否 |
| Git子模块 | 独立版本控制，易于更新 | 使用稍复杂，需要额外Git操作 | 是 |
| Fork + Pull | 可贡献回上游，社区支持 | 需要维护公开仓库，流程复杂 | 否 |

### 2.2 Git子模块方式

使用Git子模块方式集成vnpy源码的主要步骤：

1. 在SimpleTrade项目中添加vnpy作为子模块
2. 指定使用特定的vnpy版本/分支
3. 在SimpleTrade代码中直接引用vnpy模块
4. 需要修改vnpy源码时，在子模块中进行修改并提交
5. 定期从上游同步更新

## 3. 目录结构

```
simpletrade/
├── simpletrade/            # 核心代码包
│   ├── core/               # 核心引擎和功能
│   │   ├── engine.py       # 主引擎扩展
│   │   └── app.py          # 应用基类
│   ├── apps/               # 自定义应用
│   │   ├── st_trader/      # 交易增强应用
│   │   ├── st_data/        # 数据管理应用
│   │   └── st_risk/        # 风险管理应用
│   ├── api/                # API服务
│   ├── models/             # 数据模型
│   └── utils/              # 工具函数
├── vnpy/                   # vnpy源码(Git子模块)
├── docs/                   # 项目文档
├── tests/                  # 测试代码
├── scripts/                # 脚本工具
│   ├── setup_vnpy.py       # vnpy环境配置脚本
│   └── update_vnpy.py      # vnpy更新脚本
├── ui/                     # UI设计和原型
├── .gitmodules             # Git子模块配置
├── setup.py                # 项目安装脚本
└── README.md               # 项目说明
```

## 4. 集成步骤

### 4.1 添加vnpy子模块

```bash
# 在SimpleTrade项目根目录下执行
git submodule add https://github.com/vnpy/vnpy.git
cd vnpy
git checkout master  # 使用最新版本
cd ..
git add .gitmodules vnpy
git commit -m "Add vnpy as submodule with latest master version"
```

### 4.2 安装vnpy依赖

创建`scripts/setup_vnpy.py`脚本，用于安装vnpy依赖：

```python
import os
import subprocess
import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
VNPY_DIR = ROOT_DIR / "vnpy"

def install_dependencies():
    """安装vnpy依赖"""
    # 检查vnpy目录是否存在
    if not VNPY_DIR.exists():
        print(f"Error: vnpy directory not found at {VNPY_DIR}")
        return False

    # 安装基础依赖
    requirements_file = VNPY_DIR / "requirements.txt"
    if requirements_file.exists():
        print(f"Installing dependencies from {requirements_file}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])

    # 安装额外依赖(按需选择)
    install_talib()
    install_ibapi()

    print("Dependencies installation completed.")
    return True

def install_talib():
    """安装TA-Lib"""
    try:
        import talib
        print("TA-Lib already installed.")
    except ImportError:
        print("Installing TA-Lib...")
        # 根据操作系统安装TA-Lib
        if sys.platform == "win32":
            # Windows
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--index-url=https://pypi.tuna.tsinghua.edu.cn/simple", "numpy"
            ])
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-f", "https://download.lfd.uci.edu/pythonlibs/archived/cp39/TA_Lib-0.4.24-cp39-cp39-win_amd64.whl", "TA-Lib"
            ])
        elif sys.platform == "darwin":
            # macOS
            subprocess.check_call(["brew", "install", "ta-lib"])
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "TA-Lib"
            ])
        else:
            # Linux
            subprocess.check_call(["apt-get", "install", "-y", "ta-lib"])
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "TA-Lib"
            ])

def install_ibapi():
    """安装IB API"""
    try:
        import ibapi
        print("IB API already installed.")
    except ImportError:
        print("Installing IB API...")
        ibapi_dir = VNPY_DIR / "vnpy" / "api" / "ib" / "ibapi"
        if ibapi_dir.exists():
            os.chdir(ibapi_dir)
            subprocess.check_call([
                sys.executable, "setup.py", "install"
            ])
        else:
            print(f"Warning: IB API directory not found at {ibapi_dir}")

if __name__ == "__main__":
    install_dependencies()
```

### 4.3 创建主引擎扩展

创建`simpletrade/core/engine.py`文件，扩展vnpy的MainEngine：

```python
from vnpy.trader.engine import MainEngine
from vnpy.event import EventEngine, Event

class STMainEngine(MainEngine):
    """SimpleTrade主引擎"""

    def __init__(self, event_engine=None):
        """初始化"""
        if event_engine is None:
            event_engine = EventEngine()
        super().__init__(event_engine)

        # 添加SimpleTrade特有的功能
        self.st_engines = {}

        # 注册事件处理函数
        self.register_event()

    def register_event(self):
        """注册事件处理函数"""
        self.event_engine.register("eLog", self.process_log_event)

    def process_log_event(self, event):
        """处理日志事件"""
        log = event.data
        # 可以添加自定义日志处理逻辑，如保存到数据库等

    def add_st_engine(self, engine_name, engine):
        """添加SimpleTrade引擎"""
        if engine_name in self.st_engines:
            return

        self.st_engines[engine_name] = engine

    def get_st_engine(self, engine_name):
        """获取SimpleTrade引擎"""
        return self.st_engines.get(engine_name, None)

    def connect(self, setting, gateway_name):
        """扩展连接方法，添加额外功能"""
        # 添加前置处理，如连接日志记录
        print(f"Connecting to {gateway_name}...")

        # 调用原始连接方法
        result = super().connect(setting, gateway_name)

        # 添加后置处理，如连接状态检查
        if result:
            print(f"Connected to {gateway_name} successfully.")
        else:
            print(f"Failed to connect to {gateway_name}.")

        return result
```

### 4.4 创建应用基类

创建`simpletrade/core/app.py`文件，定义SimpleTrade应用基类：

```python
from pathlib import Path
from vnpy.trader.app import BaseApp
from vnpy.trader.engine import BaseEngine

class STBaseApp(BaseApp):
    """SimpleTrade基础应用类"""

    app_type = "st"  # SimpleTrade应用类型
    app_name = ""    # 应用名称
    app_module = ""  # 应用模块
    app_path = ""    # 应用路径
    display_name = ""  # 显示名称
    engine_class = None  # 引擎类
    widget_class = None  # 界面类

    def __init__(self, main_engine, event_engine):
        """初始化"""
        super().__init__(main_engine, event_engine)

class STBaseEngine(BaseEngine):
    """SimpleTrade基础引擎类"""

    def __init__(self, main_engine, event_engine, app_name):
        """初始化"""
        super().__init__(main_engine, event_engine, app_name)

        # 添加到主引擎的ST引擎列表
        if hasattr(main_engine, "add_st_engine"):
            main_engine.add_st_engine(app_name, self)
```

### 4.5 创建示例应用

创建交易增强应用示例：

```
simpletrade/apps/st_trader/
├── __init__.py
├── engine.py
└── widget.py
```

`simpletrade/apps/st_trader/__init__.py`:

```python
from pathlib import Path

from simpletrade.core.app import STBaseApp
from .engine import STTraderEngine
from .widget import STTraderWidget

APP_NAME = "st_trader"

class STTraderApp(STBaseApp):
    """SimpleTrade交易增强应用"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "ST交易增强"
    engine_class = STTraderEngine
    widget_class = STTraderWidget
```

`simpletrade/apps/st_trader/engine.py`:

```python
from simpletrade.core.app import STBaseEngine
from vnpy.trader.object import OrderRequest, CancelRequest
from vnpy.trader.constant import Direction, Offset, OrderType
from vnpy.event import Event

class STTraderEngine(STBaseEngine):
    """SimpleTrade交易增强引擎"""

    def __init__(self, main_engine, event_engine):
        """初始化"""
        super().__init__(main_engine, event_engine, "st_trader")

        # 注册事件处理函数
        self.register_event()

    def register_event(self):
        """注册事件处理函数"""
        self.event_engine.register("eOrder", self.process_order_event)
        self.event_engine.register("eTrade", self.process_trade_event)

    def process_order_event(self, event):
        """处理订单事件"""
        order = event.data
        # 处理订单逻辑

    def process_trade_event(self, event):
        """处理成交事件"""
        trade = event.data
        # 处理成交逻辑

    def send_order(self, symbol, exchange, direction, offset, price, volume, gateway_name):
        """发送订单"""
        req = OrderRequest(
            symbol=symbol,
            exchange=exchange,
            direction=direction,
            offset=offset,
            type=OrderType.LIMIT,
            price=price,
            volume=volume
        )
        return self.main_engine.send_order(req, gateway_name)

    def cancel_order(self, order_id, gateway_name):
        """撤销订单"""
        req = CancelRequest(
            orderid=order_id
        )
        return self.main_engine.cancel_order(req, gateway_name)
```

`simpletrade/apps/st_trader/widget.py`:

```python
from vnpy.trader.ui import QtWidgets

class STTraderWidget(QtWidgets.QWidget):
    """SimpleTrade交易增强界面"""

    def __init__(self, main_engine, event_engine):
        """初始化"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        self.engine = main_engine.get_engine("st_trader")

        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("ST交易增强")
        self.resize(1000, 600)

        # 创建界面组件
        label = QtWidgets.QLabel("ST交易增强界面")

        # 设置布局
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(label)
        self.setLayout(vbox)
```

### 4.6 创建主程序入口

创建`simpletrade/main.py`文件，作为程序入口：

```python
from vnpy.event import EventEngine
from simpletrade.core.engine import STMainEngine

# 导入SimpleTrade应用
from simpletrade.apps.st_trader import STTraderApp
from simpletrade.apps.st_data import STDataApp
from simpletrade.apps.st_risk import STRiskApp

def main():
    """SimpleTrade主程序入口"""
    # 创建事件引擎
    event_engine = EventEngine()

    # 创建SimpleTrade主引擎
    main_engine = STMainEngine(event_engine)

    # 加载SimpleTrade应用
    main_engine.add_app(STTraderApp)
    main_engine.add_app(STDataApp)
    main_engine.add_app(STRiskApp)

    # 加载vnpy内置应用（按需选择）
    main_engine.add_app("cta_strategy")  # CTA策略

    # 启动API服务
    # TODO: 实现API服务启动逻辑

    # 保持主程序运行
    import time
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
```

## 5. 版本控制策略

### 5.1 vnpy版本管理

1. **固定版本**: 使用特定的vnpy版本，如v4.0.0
2. **版本锁定**: 在项目中记录使用的vnpy提交哈希
3. **更新策略**: 定期评估vnpy更新，选择性合并有价值的更新

### 5.2 修改管理

1. **修改记录**: 在`docs/vnpy_modifications.md`中记录所有对vnpy源码的修改
2. **分支管理**: 在vnpy子模块中创建simpletrade分支进行修改
3. **提交规范**: 使用明确的提交信息，如`[MOD] 修改XXX功能以支持XXX`

### 5.3 更新流程

创建`scripts/update_vnpy.py`脚本，用于更新vnpy源码：

```python
import subprocess
import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
VNPY_DIR = ROOT_DIR / "vnpy"

def update_vnpy(target_version=None):
    """更新vnpy源码"""
    # 检查vnpy目录是否存在
    if not VNPY_DIR.exists():
        print(f"Error: vnpy directory not found at {VNPY_DIR}")
        return False

    # 进入vnpy目录
    cwd = Path.cwd()
    os.chdir(VNPY_DIR)

    try:
        # 获取当前版本
        current_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"]
        ).decode("utf-8").strip()
        print(f"Current vnpy commit: {current_commit}")

        # 获取远程更新
        subprocess.check_call(["git", "fetch", "origin"])

        if target_version:
            # 切换到指定版本
            subprocess.check_call(["git", "checkout", target_version])
            print(f"Switched to vnpy version: {target_version}")
        else:
            # 获取最新版本
            subprocess.check_call(["git", "checkout", "master"])
            subprocess.check_call(["git", "pull"])
            latest_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"]
            ).decode("utf-8").strip()
            print(f"Updated to latest vnpy commit: {latest_commit}")

        # 返回项目根目录
        os.chdir(cwd)

        # 更新子模块引用
        subprocess.check_call(
            ["git", "add", "vnpy"],
            cwd=ROOT_DIR
        )

        print("vnpy update completed. Please commit the changes.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error updating vnpy: {e}")
        # 返回项目根目录
        os.chdir(cwd)
        return False

if __name__ == "__main__":
    # 解析命令行参数
    target_version = None
    if len(sys.argv) > 1:
        target_version = sys.argv[1]

    update_vnpy(target_version)
```

## 6. 依赖管理

### 6.1 项目依赖

在`setup.py`中定义项目依赖：

```python
from setuptools import setup, find_packages

setup(
    name="simpletrade",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # 基础依赖
        "numpy",
        "pandas",
        "matplotlib",
        # API服务依赖
        "fastapi",
        "uvicorn",
        # 数据库依赖
        "sqlalchemy",
        # 其他依赖
        "pyqt5",
    ],
    python_requires=">=3.7",
)
```

### 6.2 开发环境

创建`requirements-dev.txt`文件，定义开发环境依赖：

```
# 测试工具
pytest
pytest-cov
# 代码质量工具
flake8
black
isort
# 文档工具
sphinx
sphinx-rtd-theme
# 其他开发工具
pre-commit
```

## 7. 测试策略

### 7.1 单元测试

为核心组件编写单元测试：

```python
# tests/core/test_engine.py
import unittest
from unittest.mock import MagicMock, patch

from simpletrade.core.engine import STMainEngine
from vnpy.event import EventEngine

class TestSTMainEngine(unittest.TestCase):
    """测试SimpleTrade主引擎"""

    def setUp(self):
        """测试前准备"""
        self.event_engine = EventEngine()
        self.main_engine = STMainEngine(self.event_engine)

    def tearDown(self):
        """测试后清理"""
        self.main_engine.close()

    def test_add_st_engine(self):
        """测试添加ST引擎"""
        # 创建模拟引擎
        mock_engine = MagicMock()

        # 添加引擎
        self.main_engine.add_st_engine("test_engine", mock_engine)

        # 验证引擎已添加
        self.assertIn("test_engine", self.main_engine.st_engines)
        self.assertEqual(self.main_engine.st_engines["test_engine"], mock_engine)

    def test_get_st_engine(self):
        """测试获取ST引擎"""
        # 创建模拟引擎
        mock_engine = MagicMock()

        # 添加引擎
        self.main_engine.add_st_engine("test_engine", mock_engine)

        # 获取引擎
        engine = self.main_engine.get_st_engine("test_engine")

        # 验证获取的引擎
        self.assertEqual(engine, mock_engine)

        # 测试获取不存在的引擎
        engine = self.main_engine.get_st_engine("non_existent_engine")
        self.assertIsNone(engine)

    @patch("vnpy.trader.engine.MainEngine.connect")
    def test_connect(self, mock_connect):
        """测试连接方法"""
        # 设置模拟返回值
        mock_connect.return_value = True

        # 调用连接方法
        setting = {"username": "test", "password": "test"}
        result = self.main_engine.connect(setting, "CTP")

        # 验证结果
        self.assertTrue(result)
        mock_connect.assert_called_once_with(setting, "CTP")
```

### 7.2 集成测试

为应用模块编写集成测试：

```python
# tests/apps/test_st_trader.py
import unittest
from unittest.mock import MagicMock, patch

from simpletrade.core.engine import STMainEngine
from simpletrade.apps.st_trader import STTraderApp
from vnpy.event import EventEngine
from vnpy.trader.constant import Direction, Offset, Exchange

class TestSTTraderApp(unittest.TestCase):
    """测试SimpleTrade交易增强应用"""

    def setUp(self):
        """测试前准备"""
        self.event_engine = EventEngine()
        self.main_engine = STMainEngine(self.event_engine)
        self.main_engine.add_app(STTraderApp)
        self.trader_engine = self.main_engine.get_engine("st_trader")

    def tearDown(self):
        """测试后清理"""
        self.main_engine.close()

    @patch("vnpy.trader.engine.MainEngine.send_order")
    def test_send_order(self, mock_send_order):
        """测试发送订单"""
        # 设置模拟返回值
        mock_send_order.return_value = "test_orderid"

        # 调用发送订单方法
        orderid = self.trader_engine.send_order(
            symbol="AAPL",
            exchange=Exchange.SMART,
            direction=Direction.LONG,
            offset=Offset.OPEN,
            price=150.0,
            volume=100,
            gateway_name="IB"
        )

        # 验证结果
        self.assertEqual(orderid, "test_orderid")
        mock_send_order.assert_called_once()

    @patch("vnpy.trader.engine.MainEngine.cancel_order")
    def test_cancel_order(self, mock_cancel_order):
        """测试撤销订单"""
        # 设置模拟返回值
        mock_cancel_order.return_value = True

        # 调用撤销订单方法
        result = self.trader_engine.cancel_order(
            order_id="test_orderid",
            gateway_name="IB"
        )

        # 验证结果
        self.assertTrue(result)
        mock_cancel_order.assert_called_once()
```

## 8. 文档

### 8.1 注释规范

遵循以下注释规范：

1. **模块注释**: 每个Python模块开头添加模块说明
2. **类注释**: 每个类添加类说明
3. **方法注释**: 每个方法添加说明、参数和返回值注释
4. **代码注释**: 复杂逻辑添加行内注释

示例：

```python
"""
SimpleTrade主引擎模块

本模块扩展了vnpy的MainEngine，添加了SimpleTrade特有的功能。
"""

class STMainEngine(MainEngine):
    """
    SimpleTrade主引擎

    负责管理所有功能模块，包括交易接口、应用模块和SimpleTrade特有的引擎。
    """

    def connect(self, setting, gateway_name):
        """
        连接交易接口

        参数:
            setting (dict): 接口设置
            gateway_name (str): 接口名称

        返回:
            bool: 连接是否成功
        """
        # 添加前置处理
        # 这里记录连接日志
        print(f"Connecting to {gateway_name}...")

        # 调用原始连接方法
        result = super().connect(setting, gateway_name)

        # 添加后置处理
        # 这里检查连接状态
        if result:
            print(f"Connected to {gateway_name} successfully.")
        else:
            print(f"Failed to connect to {gateway_name}.")

        return result
```

### 8.2 文档更新

定期更新以下文档：

1. **vnpy_integration_guide.md**: vnpy集成指南
2. **vnpy_modifications.md**: vnpy修改记录
3. **README.md**: 项目说明

## 9. 总结

本文档详细描述了SimpleTrade项目如何集成vnpy源码，采用Git子模块方式既保持了对源码的直接控制，又便于管理和更新。通过扩展vnpy的核心组件和开发自定义应用，SimpleTrade可以在vnpy的基础上构建更加专业和个性化的交易平台。
