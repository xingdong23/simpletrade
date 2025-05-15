"""
CTA策略模块的基础功能
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from copy import copy
from enum import Enum

from vnpy.trader.constant import Direction, Interval, Offset
from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy.trader.utility import ArrayManager, BarGenerator

APP_NAME = "CtaStrategy"
STOPORDER_PREFIX = "STOP"


class StopOrderStatus(Enum):
    """停止单状态"""
    WAITING = "等待中"
    CANCELLED = "已撤销"
    TRIGGERED = "已触发"


class StopOrder:
    """停止单"""

    def __init__(
        self,
        vt_symbol: str,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float,
        strategy: Any,
        stop_orderid: str,
        lock: bool = False,
        net: bool = False
    ) -> None:
        """构造函数"""
        self.vt_symbol: str = vt_symbol
        self.direction: Direction = direction
        self.offset: Offset = offset
        self.price: float = price
        self.volume: float = volume
        self.strategy: Any = strategy
        self.stop_orderid: str = stop_orderid
        self.lock: bool = lock
        self.net: bool = net

        self.status: StopOrderStatus = StopOrderStatus.WAITING
        self.vt_orderids: List[str] = []
        self.target: float = 0


class EngineType(Enum):
    """引擎类型"""
    LIVE = "实盘"
    BACKTESTING = "回测"


class CtaTemplate(ABC):
    """CTA策略模板"""

    author: str = ""
    parameters: List[str] = []
    variables: List[str] = []

    def __init__(
        self,
        cta_engine: Any,
        strategy_name: str,
        vt_symbol: str,
        setting: dict,
    ) -> None:
        """构造函数"""
        self.cta_engine: Any = cta_engine
        self.strategy_name: str = strategy_name
        self.vt_symbol: str = vt_symbol

        self.inited: bool = False
        self.trading: bool = False
        self.pos: float = 0

        # Copy a new variables list here to avoid duplicate insert when multiple
        # strategy instances are created with the same strategy class.
        self.variables = copy(self.variables)
        self.variables.insert(0, "inited")
        self.variables.insert(1, "trading")
        self.variables.insert(2, "pos")

        self.update_setting(setting)

    def update_setting(self, setting: dict) -> None:
        """更新配置"""
        for name in self.parameters:
            if name in setting:
                setattr(self, name, setting[name])

    @classmethod
    def get_class_parameters(cls) -> dict:
        """获取策略类的参数字典"""
        class_parameters = {}
        for name in cls.parameters:
            class_parameters[name] = getattr(cls, name)
        return class_parameters

    def get_parameters(self) -> dict:
        """获取策略实例的参数字典"""
        strategy_parameters = {}
        for name in self.parameters:
            strategy_parameters[name] = getattr(self, name)
        return strategy_parameters

    def get_variables(self) -> dict:
        """获取策略实例的变量字典"""
        strategy_variables = {}
        for name in self.variables:
            strategy_variables[name] = getattr(self, name)
        return strategy_variables

    def get_data(self) -> dict:
        """获取策略数据"""
        strategy_data = {
            "strategy_name": self.strategy_name,
            "vt_symbol": self.vt_symbol,
            "class_name": self.__class__.__name__,
            "author": self.author,
            "parameters": self.get_parameters(),
            "variables": self.get_variables(),
        }
        return strategy_data

    @abstractmethod
    def on_init(self) -> None:
        """策略初始化"""
        pass

    @abstractmethod
    def on_start(self) -> None:
        """策略启动"""
        pass

    @abstractmethod
    def on_stop(self) -> None:
        """策略停止"""
        pass

    @abstractmethod
    def on_tick(self, tick: TickData) -> None:
        """Tick数据更新"""
        pass

    @abstractmethod
    def on_bar(self, bar: BarData) -> None:
        """K线数据更新"""
        pass

    def on_trade(self, trade: TradeData) -> None:
        """成交数据更新"""
        pass

    def on_order(self, order: OrderData) -> None:
        """委托数据更新"""
        pass

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """停止单数据更新"""
        pass

    def buy(
        self,
        price: float,
        volume: float,
        stop: bool = False,
        lock: bool = False,
        net: bool = False
    ) -> List[str]:
        """买入开仓"""
        return self.cta_engine.send_order(
            self,
            Direction.LONG,
            Offset.OPEN,
            price,
            volume,
            stop,
            lock,
            net
        )

    def sell(
        self,
        price: float,
        volume: float,
        stop: bool = False,
        lock: bool = False,
        net: bool = False
    ) -> List[str]:
        """卖出平仓"""
        return self.cta_engine.send_order(
            self,
            Direction.SHORT,
            Offset.CLOSE,
            price,
            volume,
            stop,
            lock,
            net
        )

    def short(
        self,
        price: float,
        volume: float,
        stop: bool = False,
        lock: bool = False,
        net: bool = False
    ) -> List[str]:
        """卖出开仓"""
        return self.cta_engine.send_order(
            self,
            Direction.SHORT,
            Offset.OPEN,
            price,
            volume,
            stop,
            lock,
            net
        )

    def cover(
        self,
        price: float,
        volume: float,
        stop: bool = False,
        lock: bool = False,
        net: bool = False
    ) -> List[str]:
        """买入平仓"""
        return self.cta_engine.send_order(
            self,
            Direction.LONG,
            Offset.CLOSE,
            price,
            volume,
            stop,
            lock,
            net
        )

    def send_order(
        self,
        direction: Direction,
        offset: Offset,
        price: float,
        volume: float,
        stop: bool = False,
        lock: bool = False,
        net: bool = False
    ) -> List[str]:
        """发送委托"""
        return self.cta_engine.send_order(
            self,
            direction,
            offset,
            price,
            volume,
            stop,
            lock,
            net
        )

    def cancel_order(self, vt_orderid: str) -> None:
        """撤销委托"""
        self.cta_engine.cancel_order(self, vt_orderid)

    def cancel_all(self) -> None:
        """全部撤单"""
        self.cta_engine.cancel_all(self)

    def write_log(self, msg: str) -> None:
        """记录日志"""
        self.cta_engine.write_log(msg, self)

    def get_engine_type(self) -> EngineType:
        """查询引擎类型"""
        return self.cta_engine.get_engine_type()

    def get_pricetick(self) -> float:
        """查询价格最小变动"""
        return self.cta_engine.get_pricetick(self)

    def load_bar(
        self,
        days: int,
        interval: Interval = Interval.MINUTE,
        callback: Callable = None,
        use_database: bool = False
    ) -> None:
        """加载历史数据"""
        self.cta_engine.load_bar(
            self.vt_symbol,
            days,
            interval,
            self.on_bar,
            use_database
        )

    def load_tick(self, days: int) -> None:
        """加载Tick数据"""
        self.cta_engine.load_tick(self.vt_symbol, days, self.on_tick)

    def put_event(self) -> None:
        """推送策略数据"""
        self.cta_engine.put_strategy_event(self)

    def send_email(self, msg: str) -> None:
        """发送邮件"""
        self.cta_engine.send_email(msg, self)

    def sync_data(self) -> None:
        """同步策略数据"""
        if self.trading:
            self.cta_engine.sync_strategy_data(self)


class CtaSignal(ABC):
    """CTA信号"""

    def __init__(self) -> None:
        """构造函数"""
        self.pos = 0

    @abstractmethod
    def on_tick(self, tick: TickData) -> None:
        """Tick数据更新"""
        pass

    @abstractmethod
    def on_bar(self, bar: BarData) -> None:
        """K线数据更新"""
        pass


class TargetPosTemplate(CtaTemplate):
    """目标持仓模板"""

    tick_add = 1
    last_tick = None

    def __init__(
        self,
        cta_engine: Any,
        strategy_name: str,
        vt_symbol: str,
        setting: dict
    ) -> None:
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.active_orderids = []
        self.cancel_orderids = []
        self.target_pos = 0

    def on_tick(self, tick: TickData) -> None:
        """Tick数据更新"""
        self.last_tick = tick

        if self.trading:
            self.trade()

    def trade(self) -> None:
        """执行交易"""
        if not self.last_tick:
            return

        if self.target_pos > self.pos:
            if not self.active_orderids:
                buy_price = self.last_tick.ask_price_1 + self.tick_add
                buy_volume = self.target_pos - self.pos
                vt_orderids = self.buy(buy_price, buy_volume)
                self.active_orderids.extend(vt_orderids)
        elif self.target_pos < self.pos:
            if not self.active_orderids:
                sell_price = self.last_tick.bid_price_1 - self.tick_add
                sell_volume = self.pos - self.target_pos
                vt_orderids = self.sell(sell_price, sell_volume)
                self.active_orderids.extend(vt_orderids)

    def on_order(self, order: OrderData) -> None:
        """委托数据更新"""
        vt_orderid = order.vt_orderid

        if vt_orderid in self.active_orderids:
            if not order.is_active():
                self.active_orderids.remove(vt_orderid)

        elif vt_orderid in self.cancel_orderids:
            if not order.is_active():
                self.cancel_orderids.remove(vt_orderid)

    def on_trade(self, trade: TradeData) -> None:
        """成交数据更新"""
        if trade.direction == Direction.LONG:
            self.pos += trade.volume
        else:
            self.pos -= trade.volume

    def set_target_pos(self, target_pos) -> None:
        """设置目标持仓"""
        self.target_pos = target_pos
        self.trade()

    def cancel_all(self) -> None:
        """全部撤单"""
        for vt_orderid in self.active_orderids:
            self.cancel_order(vt_orderid)
            self.cancel_orderids.append(vt_orderid)

        self.active_orderids.clear()
