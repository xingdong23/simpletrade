"""
SimpleTrade交易增强引擎

实现交易功能的增强，包括订单管理、持仓管理等。
"""

from simpletrade.core.app import STBaseEngine
from vnpy.trader.object import OrderRequest, CancelRequest
from vnpy.trader.constant import Direction, Offset, OrderType
from vnpy.event import Event

class STTraderEngine(STBaseEngine):
    """
    SimpleTrade交易增强引擎
    
    提供交易功能的增强，包括订单管理、持仓管理等。
    """

    def __init__(self, main_engine, event_engine, engine_name: str):
        """
        初始化
        
        参数:
            main_engine (MainEngine): 主引擎
            event_engine (EventEngine): 事件引擎
            engine_name (str): 引擎名称
        """
        super().__init__(main_engine, event_engine, engine_name)
        
        # 注册事件处理函数
        self.register_event()
        
    def register_event(self):
        """注册事件处理函数"""
        self.event_engine.register("eOrder", self.process_order_event)
        self.event_engine.register("eTrade", self.process_trade_event)
        
    def process_order_event(self, event):
        """
        处理订单事件
        
        参数:
            event (Event): 订单事件
        """
        order = event.data
        # 处理订单逻辑
        print(f"收到订单事件: {order.orderid}, 状态: {order.status}")
        
    def process_trade_event(self, event):
        """
        处理成交事件
        
        参数:
            event (Event): 成交事件
        """
        trade = event.data
        # 处理成交逻辑
        print(f"收到成交事件: {trade.tradeid}, 价格: {trade.price}, 数量: {trade.volume}")
        
    def send_order(self, symbol, exchange, direction, offset, price, volume, gateway_name):
        """
        发送订单
        
        参数:
            symbol (str): 合约代码
            exchange (Exchange): 交易所
            direction (Direction): 方向
            offset (Offset): 开平
            price (float): 价格
            volume (float): 数量
            gateway_name (str): 接口名称
            
        返回:
            str: 订单ID
        """
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
        """
        撤销订单
        
        参数:
            order_id (str): 订单ID
            gateway_name (str): 接口名称
            
        返回:
            bool: 是否成功
        """
        req = CancelRequest(
            orderid=order_id
        )
        return self.main_engine.cancel_order(req, gateway_name)
