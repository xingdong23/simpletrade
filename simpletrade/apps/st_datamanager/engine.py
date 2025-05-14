"""
SimpleTrade数据管理引擎

扩展vnpy_datamanager的功能，提供数据管理功能，并添加API接口和消息指令处理。
"""


# 添加vnpy源码路径
import sys
from pathlib import Path

# 添加vnpy源码目录到Python路径
VNPY_CUSTOM_DIR = Path(__file__).parent
while VNPY_CUSTOM_DIR.name != "simpletrade" and VNPY_CUSTOM_DIR != VNPY_CUSTOM_DIR.parent:
    VNPY_CUSTOM_DIR = VNPY_CUSTOM_DIR.parent
VNPY_CUSTOM_DIR = VNPY_CUSTOM_DIR.parent / "vnpy_custom"
if VNPY_CUSTOM_DIR.exists() and str(VNPY_CUSTOM_DIR) not in sys.path:
    sys.path.insert(0, str(VNPY_CUSTOM_DIR))
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import time # 导入 time 模块
import pandas as pd # 添加 pandas 导入
import traceback # 添加 traceback 导入
from pathlib import Path

# 导入数据导入器
from simpletrade.apps.st_datamanager.importers.qlib_importer import QlibDataImporter

# 导入vnpy相关模块
from vnpy.trader.object import BarData, TickData, HistoryRequest
from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.database import get_database

# 获取数据库对象
database_manager = get_database()
from vnpy.trader.utility import extract_vt_symbol

from simpletrade.core.app import STBaseEngine

# 移除 vnpy_datamanager 的导入和检查
# try:
#     from vnpy_datamanager.engine import ManagerEngine
#     HAS_DATAMANAGER = True
# except ImportError:
#     HAS_DATAMANAGER = False
#     ManagerEngine = object  # 类型提示用

class STDataManagerEngine(STBaseEngine):
    """SimpleTrade数据管理引擎"""

    def __init__(self, main_engine, event_engine, engine_name: str):
        """初始化"""
        super().__init__(main_engine, event_engine, engine_name)

        # 移除原始 DataManager 引擎的实例化
        # self.original_engine = None
        # if HAS_DATAMANAGER:
        #     self.original_engine = ManagerEngine(main_engine, event_engine)
        #     self.write_log("vnpy_datamanager引擎已加载")
        # else:
        #     self.write_log("警告：vnpy_datamanager未安装，部分功能可能不可用")
        self.write_log("STDataManagerEngine 初始化完成。") # 添加简单的初始化日志

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
        self.main_engine.write_log(msg, source=self.engine_name)

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

    # ---- 新增：数据概览查询 ----
    def get_bar_overview(self) -> List[Any]:
        """获取所有K线数据的概览"""
        return database_manager.get_bar_overview()

    def get_tick_overview(self) -> List[Any]:
        """获取所有Tick数据的概览"""
        return database_manager.get_tick_overview()

    # ---- 数据下载功能 ----

    def download_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: Optional[datetime] = None,
        gateway_name: str = "TIGER" # 默认使用 TIGER, 或许可以设为可配置
    ) -> bool:
        """下载K线数据"""
        self.write_log(f"收到K线数据下载请求: {symbol=}, {exchange=}, {interval=}, {start=}, {end=}, {gateway_name=}")

        if end is None:
            end = datetime.now()
            self.write_log(f"结束时间未指定，使用当前时间: {end}")

        # 检查可用的网关
        all_gateways = self.main_engine.get_all_gateway_names()
        self.write_log(f"可用的网关: {all_gateways}")

        # 从 main_engine 获取 gateway 实例
        gateway = self.main_engine.get_gateway(gateway_name)
        if not gateway:
            self.write_log(f"错误：找不到名为 {gateway_name} 的 Gateway 实例。")
            return False

        # 检查 Gateway 是否已连接（通过检查核心客户端是否初始化）
        # 并实现按需连接
        connected = False
        if hasattr(gateway, "quote_client") and gateway.quote_client is not None: # 检查 quote_client 是否已初始化
            self.write_log(f"Gateway {gateway_name} 已连接。")
            connected = True
        else:
            self.write_log(f"Gateway {gateway_name} 未连接，尝试连接...")
            try:
                self.main_engine.connect({}, gateway_name)
                # 再次检查连接是否成功
                if hasattr(gateway, "quote_client") and gateway.quote_client is not None:
                    self.write_log(f"Gateway {gateway_name} 连接成功。")
                    connected = True
                    time.sleep(1) # 短暂等待，确保内部状态稳定
                else:
                    self.write_log(f"错误：调用 main_engine.connect 后，Gateway {gateway_name} 仍然未初始化客户端。")
            except Exception as e:
                self.write_log(f"连接 Gateway {gateway_name} 时出错：{e}")
                import traceback
                traceback.print_exc()

        if not connected:
            return False # 如果未连接或连接失败，则无法下载

        # 检查 gateway 是否有 query_history 方法 (有些 gateway 可能不支持)
        if not hasattr(gateway, "query_history") or not callable(gateway.query_history):
             self.write_log(f"错误：Gateway {gateway_name} 不支持历史数据查询 (缺少 query_history 方法)。")
             return False

        # 创建历史数据请求
        req = HistoryRequest(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start=start,
            end=end
        )

        # 发送请求到 gateway
        try:
            gateway.query_history(req)
            self.write_log(f"已向 Gateway {gateway_name} 发送历史数据下载请求: {req}")
            # 注意：这里只表示请求已发送，数据是异步下载和存储的。
            # 实际是否成功下载需要通过事件监听或后续查询数据库确认。
            return True
        except Exception as e:
            self.write_log(f"向 Gateway {gateway_name} 发送下载请求时出错：{e}")
            import traceback
            traceback.print_exc()
            return False

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
        """从CSV导入K线数据"""
        self.write_log(f"开始从CSV导入数据: {file_path}, 合约: {symbol}.{exchange.value}, 周期: {interval.value}")

        # 1. 检查文件是否存在
        if not os.path.exists(file_path):
            msg = f"错误：CSV文件不存在 {file_path}"
            self.write_log(msg)
            return False, msg

        # 2. 使用 pandas 读取文件
        try:
            # 显式指定dtype为str防止pandas自动类型推断导致问题, keep_default_na=False 防止空字符串被读为 NaN
            df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
            self.write_log(f"成功读取CSV文件: {file_path}, 共 {len(df)} 行")
        except Exception as e:
            msg = f"错误：读取CSV文件失败 {file_path} - {e}"
            self.write_log(msg)
            traceback.print_exc()
            return False, msg

        # 3. 解析数据行，创建 BarData 对象列表
        bars: List[BarData] = []
        imported_count = 0
        failed_count = 0

        # 获取vnpy gateway实例名称，BarData需要gateway_name
        # 暂定使用默认的TIGER, 或许可以从配置读取或作为参数传入
        gateway_name = "TIGER"

        required_headers = {
            datetime_head, open_head, high_head, low_head,
            close_head, volume_head, open_interest_head
        }
        if not required_headers.issubset(df.columns):
             missing_headers = required_headers - set(df.columns)
             msg = f"错误：CSV文件缺少必要的列: {missing_headers}"
             self.write_log(msg)
             return False, msg

        for index, row in df.iterrows():
            try:
                # 解析时间戳
                dt_str = row[datetime_head]
                dt = datetime.strptime(dt_str, datetime_format)

                # 解析价格和成交量/持仓量，处理空字符串或非数字值
                # 尝试转换为浮点数，如果失败（例如空字符串），则设为 0.0
                open_price = float(row[open_head]) if row[open_head] else 0.0
                high_price = float(row[high_head]) if row[high_head] else 0.0
                low_price = float(row[low_head]) if row[low_head] else 0.0
                close_price = float(row[close_head]) if row[close_head] else 0.0
                volume = float(row[volume_head]) if row[volume_head] else 0.0
                open_interest = float(row[open_interest_head]) if row[open_interest_head] else 0.0

                # 创建BarData对象
                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    datetime=dt,
                    interval=interval,
                    volume=volume,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    open_interest=open_interest,
                    gateway_name=gateway_name # BarData 需要 gateway_name
                )
                bars.append(bar)
                imported_count += 1
            except ValueError as ve:
                failed_count += 1
                self.write_log(f"警告：解析CSV第 {index + 2} 行数据失败 (值错误): {row.to_dict()} - {ve}")
            except KeyError as ke:
                failed_count += 1
                self.write_log(f"警告：解析CSV第 {index + 2} 行数据失败 (列名错误): {row.to_dict()} - {ke}")
            except Exception as e:
                failed_count += 1
                self.write_log(f"警告：解析CSV第 {index + 2} 行数据失败 (未知错误): {row.to_dict()} - {e}")
                traceback.print_exc()


        if not bars:
            msg = "错误：未能从CSV文件中解析出任何有效的K线数据。"
            if failed_count > 0:
                msg += f" (共失败 {failed_count} 行)"
            self.write_log(msg)
            return False, msg

        # 4. 调用 database_manager.save_bar_data() 保存数据
        try:
            database_manager.save_bar_data(bars)
            success_msg = f"成功导入 {imported_count} 条K线数据到数据库。"
            if failed_count > 0:
                success_msg += f" (跳过 {failed_count} 条错误数据)"
            self.write_log(success_msg)
            return True, success_msg
        except Exception as e:
            msg = f"错误：保存导入的K线数据到数据库时失败 - {e}"
            self.write_log(msg)
            traceback.print_exc()
            return False, msg

    def import_data_from_qlib(
        self,
        qlib_dir: str,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[bool, str]:
        """从Qlib格式导入K线数据"""
        self.write_log(f"开始从Qlib导入数据: {qlib_dir}, 合约: {symbol}.{exchange.value}, 周期: {interval.value}")

        # 1. 检查目录是否存在
        if not os.path.exists(qlib_dir):
            msg = f"错误：Qlib数据目录不存在 {qlib_dir}"
            self.write_log(msg)
            return False, msg

        # 2. 使用QlibDataImporter导入数据
        try:
            importer = QlibDataImporter()
            success, message, bars = importer.import_data(
                qlib_dir=qlib_dir,
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start_date=start_date,
                end_date=end_date
            )

            if not success or not bars:
                self.write_log(f"从Qlib导入数据失败: {message}")
                return False, message

            # 3. 保存数据到数据库
            try:
                database_manager.save_bar_data(bars)
                success_msg = f"成功从Qlib导入 {len(bars)} 条K线数据到数据库。"
                self.write_log(success_msg)
                return True, success_msg
            except Exception as e:
                msg = f"错误：保存从Qlib导入的K线数据到数据库时失败 - {e}"
                self.write_log(msg)
                traceback.print_exc()
                return False, msg

        except Exception as e:
            msg = f"错误：从Qlib导入数据时发生异常 - {e}"
            self.write_log(msg)
            traceback.print_exc()
            return False, msg

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
