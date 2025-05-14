#!/bin/bash

# 检测系统环境
echo "Checking system environment..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "Detected OS: $NAME $VERSION_ID"
fi

# 创建基本认证用户
if [ ! -f /etc/nginx/.htpasswd ]; then
    echo "Creating basic auth user..."
    echo "admin:$(openssl passwd -apr1 admin123)" > /etc/nginx/.htpasswd
fi

# 记录当前版本
if [ -n "$VERSION" ]; then
    echo "$VERSION" > /app/panel/version.txt
else
    echo "unknown" > /app/panel/version.txt
fi

# 记录部署时间
date > /app/panel/deploy_time.txt

# 创建部署脚本
cat > /app/deploy.sh << 'EOF'
#!/bin/bash

# 部署脚本
# 用法: ./deploy.sh [version]

# 记录部署开始
LOG_FILE="/app/logs/deploy_$(date +%Y%m%d_%H%M%S).log"
echo "===== 部署开始 $(date) =====" | tee -a "$LOG_FILE"

# 如果提供了版本参数，则使用该版本
if [ -n "$1" ]; then
    VERSION="$1"
    echo "使用指定版本: $VERSION" | tee -a "$LOG_FILE"
else
    VERSION="latest"
    echo "使用默认版本: $VERSION" | tee -a "$LOG_FILE"
fi

# 更新版本信息
echo "$VERSION" > /app/panel/version.txt
date > /app/panel/deploy_time.txt

echo "===== 部署完成 $(date) =====" | tee -a "$LOG_FILE"
echo "当前版本: $VERSION" | tee -a "$LOG_FILE"
EOF

chmod +x /app/deploy.sh

# 创建日志目录
mkdir -p /app/logs

# 删除ta-lib相关文件
echo "Removing ta-lib related files..."
rm -rf /app/logs/ta-lib /app/logs/ta-lib-0.4.0-src.tar.gz

# 启动部署API服务器
echo "Starting deployment API server..."
python3.9 /app/panel/deploy.py > /app/logs/deploy_panel.log 2>&1 &

# 启动部署处理服务器
echo "Starting deployment handler server..."
python3.9 /app/panel/deploy_handler.py > /app/logs/deploy_handler.log 2>&1 &

# 启动后端服务
echo "Starting backend service..."
cd /app/backend

# 确保vnpy_custom目录存在
if [ ! -d "/app/backend/vnpy_custom/vnpy/trader" ]; then
    echo "Creating vnpy_custom directory structure..."
    mkdir -p /app/backend/vnpy_custom/vnpy/event
    mkdir -p /app/backend/vnpy_custom/vnpy/trader

    # 创建event/__init__.py文件
    cat > /app/backend/vnpy_custom/vnpy/event/__init__.py << 'EOF'
from collections import defaultdict
from queue import Empty, Queue
from threading import Thread
from time import sleep
from typing import Any, Callable, List

class Event:
    """事件对象"""

    def __init__(self, type: str, data: Any = None) -> None:
        """构造函数"""
        self.type = type
        self.data = data


class EventEngine:
    """事件驱动引擎"""

    def __init__(self, interval: float = 0.1) -> None:
        """构造函数"""
        self._interval = interval
        self._queue = Queue()
        self._active = False
        self._thread = Thread(target=self._run)
        self._timer = Thread(target=self._run_timer)
        self._handlers = defaultdict(list)
        self._general_handlers = []

    def _run(self) -> None:
        """运行事件处理循环"""
        while self._active:
            try:
                event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass

    def _process(self, event: Event) -> None:
        """处理事件"""
        if event.type in self._handlers:
            [handler(event) for handler in self._handlers[event.type]]

        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

    def _run_timer(self) -> None:
        """运行定时器"""
        while self._active:
            sleep(self._interval)
            event = Event("timer")
            self.put(event)

    def start(self) -> None:
        """启动引擎"""
        self._active = True
        self._thread.start()
        self._timer.start()

    def stop(self) -> None:
        """停止引擎"""
        self._active = False
        self._timer.join()
        self._thread.join()

    def put(self, event: Event) -> None:
        """放入事件"""
        self._queue.put(event)

    def register(self, type: str, handler: Callable) -> None:
        """注册事件处理函数"""
        handler_list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type: str, handler: Callable) -> None:
        """注销事件处理函数"""
        handler_list = self._handlers[type]

        if handler in handler_list:
            handler_list.remove(handler)

        if not handler_list:
            del self._handlers[type]

    def register_general(self, handler: Callable) -> None:
        """注册通用事件处理函数"""
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler: Callable) -> None:
        """注销通用事件处理函数"""
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)
EOF

    # 创建vnpy_custom/__init__.py文件
    touch /app/backend/vnpy_custom/__init__.py

    # 创建vnpy_custom/vnpy/__init__.py文件
    touch /app/backend/vnpy_custom/vnpy/__init__.py

    # 创建trader/__init__.py文件
    touch /app/backend/vnpy_custom/vnpy/trader/__init__.py

    # 创建trader/setting.py文件
    cat > /app/backend/vnpy_custom/vnpy/trader/setting.py << 'EOF'
"""
全局设置
"""

from pathlib import Path
from typing import Dict, Any

# 默认设置
SETTINGS: Dict[str, Any] = {
    "font.family": "Arial",
    "font.size": 12,

    "log.active": True,
    "log.level": "INFO",
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "database.timezone": "Asia/Shanghai",
    "database.driver": "sqlite",
    "database.database": "database.db",
    "database.host": "localhost",
    "database.port": 3306,
    "database.user": "root",
    "database.password": "",
    "database.authentication_source": "admin",
}

# 导入本地配置
SETTING_FILENAME: str = "vt_setting.json"
SETTING_FILEPATH: Path = Path.cwd().joinpath(SETTING_FILENAME)

if SETTING_FILEPATH.exists():
    import json

    with open(SETTING_FILEPATH, mode="r") as f:
        local_setting = json.load(f)
    SETTINGS.update(local_setting)
EOF

    # 创建trader/gateway.py文件
    cat > /app/backend/vnpy_custom/vnpy/trader/gateway.py << 'EOF'
"""
网关接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable

class BaseGateway(ABC):
    """交易网关基类"""

    def __init__(self, event_engine, gateway_name: str) -> None:
        """构造函数"""
        self.event_engine = event_engine
        self.gateway_name: str = gateway_name

    def on_event(self, type: str, data: Any = None) -> None:
        """推送事件"""
        event = Event(type, data)
        self.event_engine.put(event)

    def write_log(self, msg: str) -> None:
        """记录日志"""
        log = LogData(
            gateway_name=self.gateway_name,
            msg=msg
        )
        event = Event("LOG", log)
        self.event_engine.put(event)

    @abstractmethod
    def connect(self, setting: dict) -> None:
        """连接交易接口"""
        pass

    @abstractmethod
    def close(self) -> None:
        """关闭交易接口"""
        pass

    @abstractmethod
    def subscribe(self, req: SubscribeRequest) -> None:
        """订阅行情"""
        pass

    @abstractmethod
    def send_order(self, req: OrderRequest) -> str:
        """委托下单"""
        pass

    @abstractmethod
    def cancel_order(self, req: CancelRequest) -> None:
        """委托撤单"""
        pass

    @abstractmethod
    def query_account(self) -> None:
        """查询资金"""
        pass

    @abstractmethod
    def query_position(self) -> None:
        """查询持仓"""
        pass

# 为了避免循环导入，这里简单定义一些必要的类
class Event:
    def __init__(self, type: str, data: Any = None) -> None:
        self.type = type
        self.data = data

class LogData:
    def __init__(self, gateway_name: str, msg: str) -> None:
        self.gateway_name = gateway_name
        self.msg = msg

class SubscribeRequest:
    def __init__(self) -> None:
        self.symbol = ""
        self.exchange = None

class OrderRequest:
    def __init__(self) -> None:
        self.symbol = ""
        self.exchange = None
        self.price = 0.0
        self.volume = 0.0
        self.type = None
        self.direction = None
        self.offset = None
        self.reference = ""

class CancelRequest:
    def __init__(self) -> None:
        self.orderid = ""
        self.symbol = ""
        self.exchange = None
EOF
fi

# 修改initialization.py文件使用vnpy_custom中的模块
sed -i 's/from vnpy.event import EventEngine/from vnpy_custom.vnpy.event import EventEngine/' /app/backend/simpletrade/core/initialization.py
sed -i 's/from vnpy.trader.setting import SETTINGS/from vnpy_custom.vnpy.trader.setting import SETTINGS/' /app/backend/simpletrade/core/initialization.py
sed -i 's/from vnpy.trader.gateway import BaseGateway/from vnpy_custom.vnpy.trader.gateway import BaseGateway/' /app/backend/simpletrade/core/initialization.py

# 启动后端服务
python3.9 -m simpletrade.main > /app/logs/backend.log 2>&1 &

# 创建前端日志的符号链接
ln -sf /var/log/nginx/access.log /app/logs/frontend_access.log
ln -sf /var/log/nginx/error.log /app/logs/frontend_error.log

# 创建部署面板的符号链接
# 这是为了解决Nginx配置问题，确保/deploy/路径可访问
mkdir -p /usr/share/nginx/html/deploy
ln -sf /app/panel/* /usr/share/nginx/html/deploy/

# 启动 Nginx
echo "Starting Nginx..."
nginx -g "daemon off;"
