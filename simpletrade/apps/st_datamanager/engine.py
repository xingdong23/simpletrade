"""
SimpleTrade数据管理引擎

扩展vnpy_datamanager的功能，提供数据管理功能，并添加API接口和消息指令处理。
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.database import get_database

# 获取数据库对象
database_manager = get_database()
from vnpy.trader.utility import extract_vt_symbol

from simpletrade.core.app import STBaseEngine

# 导入vnpy_datamanager的引擎
try:
    from vnpy_datamanager.engine import ManagerEngine
    HAS_DATAMANAGER = True
except ImportError:
    HAS_DATAMANAGER = False
    ManagerEngine = object  # 类型提示用

class STDataManagerEngine(STBaseEngine):
    """SimpleTrade数据管理引擎"""

    def __init__(self, main_engine, event_engine):
        """初始化"""
        super().__init__(main_engine, event_engine, "st_datamanager")

        # 创建原始DataManager引擎实例（如果可用）
        self.original_engine = None
        if HAS_DATAMANAGER:
            self.original_engine = ManagerEngine(main_engine, event_engine)
            self.write_log("vnpy_datamanager引擎已加载")
        else:
            self.write_log("警告：vnpy_datamanager未安装，部分功能可能不可用")

        # 初始化API路由和消息指令
        self.init_api_routes()
        self.init_message_commands()

    def init_api_routes(self):
        """初始化API路由"""
        try:
            from .api import router
            self.write_log("API路由初始化成功")

            # 将路由器保存到引擎实例中，便于外部访问
            self.router = router

            # 将引擎实例注册到全局变量中，便于API访问
            # 注意：这里使用了全局变量，实际应用中可能需要更好的方式
            import sys
            sys.modules["simpletrade.apps.st_datamanager.api.engine"] = self
        except Exception as e:
            self.write_log(f"API路由初始化失败：{str(e)}")

    def init_message_commands(self):
        """初始化消息指令"""
        try:
            from .commands import DataCommandProcessor
            self.command_processor = DataCommandProcessor(self)
            self.write_log("消息指令处理器初始化成功")

            # 将指令处理器注册到消息引擎（如果存在）
            message_engine = self.main_engine.get_engine("st_message")
            if message_engine:
                message_engine.register_processor("/data", self.command_processor)
                self.write_log("消息指令处理器注册成功")
            else:
                self.write_log("警告：st_message引擎未找到，消息指令将无法使用")
        except Exception as e:
            self.write_log(f"消息指令处理器初始化失败：{str(e)}")

    def process_command(self, command_text: str) -> str:
        """处理消息指令

        这个方法可以直接调用，方便测试和开发
        """
        if hasattr(self, "command_processor"):
            return self.command_processor.process(command_text)
        else:
            return "消息指令处理器未初始化"

    def write_log(self, msg: str):
        """写入日志"""
        self.main_engine.write_log(msg, source=self.app_name)

    # ---- 数据查询功能 ----

    def get_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[BarData]:
        """获取K线数据"""
        if end is None:
            end = datetime.now()

        return database_manager.load_bar_data(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start=start,
            end=end
        )

    def get_tick_data(
        self,
        symbol: str,
        exchange: Exchange,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[TickData]:
        """获取Tick数据"""
        if end is None:
            end = datetime.now()

        return database_manager.load_tick_data(
            symbol=symbol,
            exchange=exchange,
            start=start,
            end=end
        )

    def get_available_data(self) -> List[Dict[str, Any]]:
        """获取可用的数据列表"""
        data = []

        # 获取所有K线数据的合约信息
        for interval in Interval:
            bar_symbols = database_manager.get_bar_symbols(interval)
            for vt_symbol in bar_symbols:
                symbol, exchange = extract_vt_symbol(vt_symbol)
                overview = database_manager.get_bar_overview(symbol, exchange, interval)
                if overview:
                    data.append({
                        "symbol": symbol,
                        "exchange": exchange.value,
                        "interval": interval.value,
                        "count": overview.count,
                        "start": overview.start.strftime("%Y-%m-%d %H:%M:%S"),
                        "end": overview.end.strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "bar"
                    })

        # 获取所有Tick数据的合约信息
        tick_symbols = database_manager.get_tick_symbols()
        for vt_symbol in tick_symbols:
            symbol, exchange = extract_vt_symbol(vt_symbol)
            overview = database_manager.get_tick_overview(symbol, exchange)
            if overview:
                data.append({
                    "symbol": symbol,
                    "exchange": exchange.value,
                    "count": overview.count,
                    "start": overview.start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": overview.end.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "tick"
                })

        return data

    # ---- 数据下载功能 ----

    def download_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: Optional[datetime] = None
    ) -> bool:
        """下载K线数据"""
        if not self.original_engine:
            self.write_log("错误：vnpy_datamanager未安装，无法下载数据")
            return False

        if end is None:
            end = datetime.now()

        return self.original_engine.download_bar_data(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start=start,
            end=end
        )

    # ---- 数据导入导出功能 ----

    def import_data_from_csv(
        self,
        file_path: str,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        datetime_head: str,
        open_head: str,
        high_head: str,
        low_head: str,
        close_head: str,
        volume_head: str,
        open_interest_head: str,
        datetime_format: str
    ) -> Tuple[bool, str]:
        """从CSV导入数据"""
        if not self.original_engine:
            return False, "错误：vnpy_datamanager未安装，无法导入数据"

        if not os.path.exists(file_path):
            return False, f"错误：文件不存在 {file_path}"

        try:
            result = self.original_engine.import_data_from_csv(
                file_path=file_path,
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                datetime_head=datetime_head,
                open_head=open_head,
                high_head=high_head,
                low_head=low_head,
                close_head=close_head,
                volume_head=volume_head,
                open_interest_head=open_interest_head,
                datetime_format=datetime_format
            )
            if result:
                return True, "数据导入成功"
            else:
                return False, "数据导入失败"
        except Exception as e:
            return False, f"数据导入出错：{str(e)}"

    def export_data_to_csv(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime,
        file_path: str
    ) -> Tuple[bool, str]:
        """导出数据到CSV"""
        if not os.path.exists(os.path.dirname(file_path)):
            return False, f"错误：目录不存在 {os.path.dirname(file_path)}"

        try:
            bars = self.get_bar_data(symbol, exchange, interval, start, end)
            if not bars:
                return False, "错误：未找到符合条件的数据"

            # 创建CSV文件
            with open(file_path, "w", encoding="utf-8") as f:
                # 写入表头
                f.write("datetime,open,high,low,close,volume,open_interest\n")

                # 写入数据
                for bar in bars:
                    line = f"{bar.datetime},{bar.open_price},{bar.high_price},{bar.low_price},{bar.close_price},{bar.volume},{bar.open_interest}\n"
                    f.write(line)

            return True, f"成功导出 {len(bars)} 条数据到 {file_path}"
        except Exception as e:
            return False, f"数据导出出错：{str(e)}"

    # ---- 数据管理功能 ----

    def delete_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval
    ) -> Tuple[bool, str]:
        """删除K线数据"""
        try:
            count = database_manager.delete_bar_data(
                symbol=symbol,
                exchange=exchange,
                interval=interval
            )
            return True, f"成功删除 {count} 条K线数据"
        except Exception as e:
            return False, f"删除数据出错：{str(e)}"

    def delete_tick_data(
        self,
        symbol: str,
        exchange: Exchange
    ) -> Tuple[bool, str]:
        """删除Tick数据"""
        try:
            count = database_manager.delete_tick_data(
                symbol=symbol,
                exchange=exchange
            )
            return True, f"成功删除 {count} 条Tick数据"
        except Exception as e:
            return False, f"删除数据出错：{str(e)}"
