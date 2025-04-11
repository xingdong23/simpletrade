"""
老虎证券交易接口
"""

import time
from copy import copy
from datetime import datetime, timedelta
from threading import Thread, Lock
from typing import Dict, List, Set, Any, Callable, Optional

from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.consts import Language, Currency, Market
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.trade.trade_client import TradeClient
from tigeropen.push.push_client import PushClient
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.quote.domain.market_status import MarketStatus
from tigeropen.quote.domain.quote_bar import QuoteBar
from tigeropen.quote.domain.quote_tick import QuoteTick
from tigeropen.quote.request.market_status_request import MarketStatusRequest
from tigeropen.quote.request.quote_request import OpenApiRequest
from tigeropen.quote.response.quote_bar_response import QuoteBarResponse
from tigeropen.quote.request.quote_bar_request import QuoteBarRequest
from tigeropen.push.push_client import PushClient

from vnpy.event import EventEngine
from vnpy.trader.constant import (
    Direction,
    Exchange,
    OrderType,
    Product,
    Status,
    Interval
)
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.object import (
    TickData,
    OrderData,
    TradeData,
    PositionData,
    AccountData,
    ContractData,
    BarData,
    OrderRequest,
    CancelRequest,
    SubscribeRequest,
    HistoryRequest
)

# 老虎证券交易所映射
EXCHANGE_TIGER2VT: Dict[str, Exchange] = {
    "NYSE": Exchange.NYSE,
    "NASDAQ": Exchange.NASDAQ,
    "AMEX": Exchange.AMEX,
    "SEHK": Exchange.SEHK,
    "HKFE": Exchange.HKFE,
    "SGX": Exchange.SGX,
    "ASX": Exchange.ASX,
}
EXCHANGE_VT2TIGER: Dict[Exchange, str] = {v: k for k, v in EXCHANGE_TIGER2VT.items()}

# 老虎证券K线周期映射
INTERVAL_VT2TIGER: Dict[Interval, str] = {
    Interval.MINUTE: "min",
    Interval.HOUR: "hour",
    Interval.DAILY: "day",
    Interval.WEEKLY: "week",
}

# 老虎证券产品类型映射
PRODUCT_TIGER2VT: Dict[str, Product] = {
    "STK": Product.EQUITY,
    "OPT": Product.OPTION,
    "FUT": Product.FUTURES,
    "WAR": Product.WARRANT,
    "CASH": Product.FOREX
}

# 老虎证券订单类型映射
ORDERTYPE_VT2TIGER: Dict[OrderType, str] = {
    OrderType.LIMIT: "LMT",
    OrderType.MARKET: "MKT",
}
ORDERTYPE_TIGER2VT: Dict[str, OrderType] = {v: k for k, v in ORDERTYPE_VT2TIGER.items()}

# 老虎证券订单状态映射
STATUS_TIGER2VT: Dict[str, Status] = {
    "Submitted": Status.SUBMITTING,
    "Filled": Status.ALLTRADED,
    "Cancelled": Status.CANCELLED,
    "Inactive": Status.REJECTED,
    "PendingSubmit": Status.SUBMITTING,
    "PendingCancel": Status.CANCELLING,
    "Partial": Status.PARTTRADED,
    "Rejected": Status.REJECTED,
}

# 老虎证券方向映射
DIRECTION_VT2TIGER: Dict[Direction, str] = {
    Direction.LONG: "BUY",
    Direction.SHORT: "SELL",
}
DIRECTION_TIGER2VT: Dict[str, Direction] = {v: k for k, v in DIRECTION_VT2TIGER.items()}


class TigerGateway(BaseGateway):
    """
    VeighNa用于对接老虎证券的交易接口。
    """

    default_name: str = "TIGER"

    default_setting: Dict[str, Any] = {
        "tiger_id": "",
        "account": "",
        "private_key": "",
        "server": ["标准", "环球", "模拟"],
        "language": ["中文", "英文"],
    }

    exchanges: List[Exchange] = list(EXCHANGE_VT2TIGER.keys())

    def __init__(self, event_engine: EventEngine, gateway_name: str) -> None:
        """构造函数"""
        super().__init__(event_engine, gateway_name)

        self.tiger_id: str = ""
        self.account: str = ""
        self.server: str = ""
        self.language: str = ""
        self.private_key: str = ""

        self.quote_client: Optional[QuoteClient] = None
        self.trade_client: Optional[TradeClient] = None
        self.push_client: Optional[PushClient] = None

        self.local_orderids: Set[str] = set()
        self.orderid_tiger2vt: Dict[str, str] = {}
        self.orderid_vt2tiger: Dict[str, str] = {}

        self.subscribed: Set[str] = set()
        self.symbol_exchange_map: Dict[str, Exchange] = {}

        self.thread_quote: Thread = Thread(target=self.query_quote)
        self.thread_quote_started: bool = False
        self.thread_quote_interval: int = 10

        self.thread_trade: Thread = Thread(target=self.query_trade)
        self.thread_trade_started: bool = False
        self.thread_trade_interval: int = 10

    def connect(self, setting: Dict[str, str]) -> None:
        """连接交易接口"""
        self.tiger_id = setting["tiger_id"]
        self.account = setting["account"]
        self.private_key = setting["private_key"]

        server = setting["server"]
        if server == "标准":
            self.server = "standard"
        elif server == "环球":
            self.server = "global"
        else:
            self.server = "paper"

        language = setting["language"]
        if language == "中文":
            self.language = Language.zh_CN
        else:
            self.language = Language.en_US

        # 创建老虎证券客户端
        config = TigerOpenClientConfig(
            tiger_id=self.tiger_id,
            account=self.account,
            private_key=read_private_key(self.private_key),
            language=self.language
        )

        self.quote_client = QuoteClient(config)
        self.trade_client = TradeClient(config)
        self.push_client = PushClient(config)

        # 查询合约信息
        self.query_contract()

        # 查询账户资金
        self.query_account()

        # 查询持仓
        self.query_position()

        # 查询委托
        self.query_order()

        # 启动行情查询线程
        if not self.thread_quote_started:
            self.thread_quote_started = True
            self.thread_quote.start()

        # 启动交易查询线程
        if not self.thread_trade_started:
            self.thread_trade_started = True
            self.thread_trade.start()

        self.write_log("交易接口连接成功")

    def subscribe(self, req: SubscribeRequest) -> None:
        """订阅行情"""
        if req.symbol in self.subscribed:
            return

        # 缓存合约和交易所的映射关系
        self.symbol_exchange_map[req.symbol] = req.exchange

        # 订阅行情
        symbols = [req.symbol]
        self.quote_client.subscribe_quote(symbols)

        # 订阅推送
        self.push_client.subscribe_quote(symbols)
        self.push_client.quote_changed = self.on_quote_changed

        self.subscribed.add(req.symbol)

    def send_order(self, req: OrderRequest) -> str:
        """委托下单"""
        # 生成本地委托号
        orderid = req.symbol + "_" + str(time.time())
        self.local_orderids.add(orderid)

        # 创建委托请求
        tiger_req = {
            "account": self.account,
            "contract": {
                "symbol": req.symbol,
                "exchange": EXCHANGE_VT2TIGER[req.exchange],
                "sec_type": "STK"
            },
            "action": DIRECTION_VT2TIGER[req.direction],
            "order_type": ORDERTYPE_VT2TIGER[req.type],
            "quantity": req.volume,
            "limit_price": req.price
        }

        # 发送委托请求
        try:
            result = self.trade_client.place_order(tiger_req)
            tiger_orderid = str(result.order_id)
            self.orderid_tiger2vt[tiger_orderid] = orderid
            self.orderid_vt2tiger[orderid] = tiger_orderid
            return orderid
        except Exception as e:
            self.write_log(f"委托失败：{e}")
            return ""

    def cancel_order(self, req: CancelRequest) -> None:
        """委托撤单"""
        if req.orderid not in self.orderid_vt2tiger:
            self.write_log(f"撤单失败：找不到委托号{req.orderid}")
            return

        tiger_orderid = self.orderid_vt2tiger[req.orderid]

        try:
            self.trade_client.cancel_order(tiger_orderid)
        except Exception as e:
            self.write_log(f"撤单失败：{e}")

    def query_account(self) -> None:
        """查询账户资金"""
        try:
            assets = self.trade_client.get_assets()
            for asset in assets:
                account = AccountData(
                    accountid=self.account,
                    balance=asset.net_liquidation,
                    frozen=asset.net_liquidation - asset.available_funds,
                    gateway_name=self.gateway_name
                )
                self.on_account(account)
        except Exception as e:
            self.write_log(f"查询账户资金失败：{e}")

    def query_position(self) -> None:
        """查询持仓"""
        try:
            positions = self.trade_client.get_positions()
            for position in positions:
                pos = PositionData(
                    symbol=position.contract.symbol,
                    exchange=EXCHANGE_TIGER2VT.get(position.contract.exchange, Exchange.SMART),
                    direction=Direction.LONG if position.quantity > 0 else Direction.SHORT,
                    volume=abs(position.quantity),
                    price=position.average_cost,
                    gateway_name=self.gateway_name
                )
                self.on_position(pos)
        except Exception as e:
            self.write_log(f"查询持仓失败：{e}")

    def query_order(self) -> None:
        """查询委托"""
        try:
            orders = self.trade_client.get_orders()
            for order in orders:
                orderid = str(order.order_id)
                if orderid not in self.orderid_tiger2vt:
                    local_orderid = orderid
                    self.orderid_tiger2vt[orderid] = local_orderid
                    self.orderid_vt2tiger[local_orderid] = orderid
                else:
                    local_orderid = self.orderid_tiger2vt[orderid]

                order_data = OrderData(
                    symbol=order.contract.symbol,
                    exchange=EXCHANGE_TIGER2VT.get(order.contract.exchange, Exchange.SMART),
                    orderid=local_orderid,
                    type=ORDERTYPE_TIGER2VT.get(order.order_type, OrderType.LIMIT),
                    direction=DIRECTION_TIGER2VT.get(order.action, Direction.LONG),
                    price=order.limit_price,
                    volume=order.quantity,
                    traded=order.filled,
                    status=STATUS_TIGER2VT.get(order.status, Status.SUBMITTING),
                    datetime=datetime.fromtimestamp(order.order_time / 1000),
                    gateway_name=self.gateway_name
                )
                self.on_order(order_data)
        except Exception as e:
            self.write_log(f"查询委托失败：{e}")

    def query_contract(self) -> None:
        """查询合约"""
        # 查询美股合约
        try:
            symbols = self.quote_client.get_symbols(Market.ALL)
            for symbol in symbols:
                contract = ContractData(
                    symbol=symbol.symbol,
                    exchange=EXCHANGE_TIGER2VT.get(symbol.exchange, Exchange.SMART),
                    name=symbol.name,
                    product=PRODUCT_TIGER2VT.get(symbol.sec_type, Product.EQUITY),
                    size=1,
                    pricetick=0.01,
                    gateway_name=self.gateway_name
                )
                self.on_contract(contract)
            self.write_log("合约信息查询成功")
        except Exception as e:
            self.write_log(f"查询合约失败：{e}")

    def query_history(self, req: HistoryRequest) -> List[BarData]:
        """查询历史数据"""
        # 转换时间格式
        start_time = int(req.start.timestamp() * 1000)
        end_time = int(req.end.timestamp() * 1000)

        # 创建查询请求
        bar_req = QuoteBarRequest(
            symbol=req.symbol,
            period=INTERVAL_VT2TIGER[req.interval],
            begin_time=start_time,
            end_time=end_time
        )

        # 查询历史数据
        try:
            response = self.quote_client.get_bars(bar_req)
            bars = []
            for bar in response.items:
                dt = datetime.fromtimestamp(bar.time / 1000)
                bar_data = BarData(
                    symbol=req.symbol,
                    exchange=req.exchange,
                    datetime=dt,
                    interval=req.interval,
                    volume=bar.volume,
                    open_price=bar.open,
                    high_price=bar.high,
                    low_price=bar.low,
                    close_price=bar.close,
                    gateway_name=self.gateway_name
                )
                bars.append(bar_data)
            return bars
        except Exception as e:
            self.write_log(f"查询历史数据失败：{e}")
            return []

    def close(self) -> None:
        """关闭连接"""
        if self.thread_quote_started:
            self.thread_quote_started = False
            self.thread_quote.join()

        if self.thread_trade_started:
            self.thread_trade_started = False
            self.thread_trade.join()

    def query_quote(self) -> None:
        """查询行情"""
        while self.thread_quote_started:
            try:
                for symbol in self.subscribed:
                    exchange = self.symbol_exchange_map.get(symbol, Exchange.SMART)
                    tick = self.quote_client.get_latest_quote([symbol])
                    if not tick or not tick.items:
                        continue

                    for item in tick.items:
                        tick_data = TickData(
                            symbol=item.symbol,
                            exchange=exchange,
                            name=item.symbol,
                            volume=item.volume,
                            last_price=item.latest_price,
                            datetime=datetime.fromtimestamp(item.latest_time / 1000),
                            gateway_name=self.gateway_name
                        )
                        self.on_tick(tick_data)
            except Exception as e:
                self.write_log(f"查询行情失败：{e}")

            time.sleep(self.thread_quote_interval)

    def query_trade(self) -> None:
        """查询交易"""
        while self.thread_trade_started:
            try:
                self.query_account()
                self.query_position()
                self.query_order()
            except Exception as e:
                self.write_log(f"查询交易失败：{e}")

            time.sleep(self.thread_trade_interval)

    def on_quote_changed(self, tiger_tick: QuoteTick) -> None:
        """行情推送回调"""
        symbol = tiger_tick.symbol
        exchange = self.symbol_exchange_map.get(symbol, Exchange.SMART)

        tick = TickData(
            symbol=symbol,
            exchange=exchange,
            name=symbol,
            volume=tiger_tick.volume,
            last_price=tiger_tick.latest_price,
            datetime=datetime.fromtimestamp(tiger_tick.latest_time / 1000),
            gateway_name=self.gateway_name
        )
        self.on_tick(tick)
