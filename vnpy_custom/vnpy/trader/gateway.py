"""
网关接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable

# 定义必要的类
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
