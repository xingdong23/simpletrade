"""
SimpleTrade数据管理器

提供数据管理功能，包括数据下载、导入、导出、查询和管理。
直接使用vnpy的数据管理功能。
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

# 导入vnpy的数据模型和数据管理功能
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database

# 获取日志记录器
import logging
logger = logging.getLogger(__name__)


class DataManager:
    """数据管理器

    封装vnpy的数据管理功能，提供统一的接口。
    """

    def __init__(self, database_path: str = None):
        """初始化

        参数:
            database_path: 数据库路径，默认为空，使用vnpy的默认数据库
        """
        # 获取vnpy的数据库管理器
        self.database_manager = get_database()

        # 如果指定了数据库路径，则设置数据库路径
        if database_path:
            self.database_path = database_path
            # 注意：这里只是记录路径，实际上不会改变vnpy的数据库路径
            # 如果需要使用自定义数据库，需要在vnpy的配置文件中设置
        else:
            self.database_path = "vnpy default database"

    # ---- 数据保存功能 ----

    def save_bar_data(self, bars: List[BarData]) -> int:
        """保存K线数据

        参数:
            bars: K线数据列表

        返回:
            int: 成功保存的数据数量
        """
        if not bars:
            return 0

        # 使用vnpy的数据库管理器保存数据
        self.database_manager.save_bar_data(bars)

        return len(bars)

    def save_tick_data(self, ticks: List[TickData]) -> int:
        """保存Tick数据

        参数:
            ticks: Tick数据列表

        返回:
            int: 成功保存的数据数量
        """
        if not ticks:
            return 0

        # 使用vnpy的数据库管理器保存数据
        self.database_manager.save_tick_data(ticks)

        return len(ticks)

    # ---- 数据加载功能 ----

    def load_bar_data(
        self,
        symbol: str,
        exchange: Union[str, Exchange],
        interval: Union[str, Interval],
        start: datetime,
        end: datetime
    ) -> List[BarData]:
        """加载K线数据

        参数:
            symbol: 代码
            exchange: 交易所
            interval: 周期
            start: 开始时间
            end: 结束时间

        返回:
            List[BarData]: K线数据列表
        """
        # 确保交易所和周期是正确的类型
        if isinstance(exchange, str):
            exchange = Exchange(exchange)

        if isinstance(interval, str):
            interval = Interval(interval)

        # 使用vnpy的数据库管理器加载数据
        bars = self.database_manager.load_bar_data(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start=start,
            end=end
        )

        return bars

    def load_tick_data(
        self,
        symbol: str,
        exchange: Union[str, Exchange],
        start: datetime,
        end: datetime
    ) -> List[TickData]:
        """加载Tick数据

        参数:
            symbol: 代码
            exchange: 交易所
            start: 开始时间
            end: 结束时间

        返回:
            List[TickData]: Tick数据列表
        """
        # 确保交易所是正确的类型
        if isinstance(exchange, str):
            exchange = Exchange(exchange)

        # 使用vnpy的数据库管理器加载数据
        ticks = self.database_manager.load_tick_data(
            symbol=symbol,
            exchange=exchange,
            start=start,
            end=end
        )

        return ticks

    # ---- 数据查询功能 ----

    def get_bar_overview(self) -> List[Dict[str, Any]]:
        """获取K线数据概览

        返回:
            List[Dict[str, Any]]: K线数据概览列表
        """
        logger.info("开始获取K线数据概览...")
        overviews = []
        try:
            all_intervals = list(Interval) # 获取所有 Interval 枚举成员
            logger.info(f"检查周期: {all_intervals}")
        except Exception as e:
            logger.exception("获取 Interval 列表时出错")
            all_intervals = []
            
        for interval in all_intervals:
            logger.info(f"正在处理周期: {interval}")
            try:
                # 获取该周期的所有合约
                symbols = self.database_manager.get_bar_symbols(interval)
                logger.info(f"周期 {interval} 找到合约: {symbols}")

                # 遍历所有合约
                for vt_symbol in symbols:
                    logger.info(f"处理合约: {vt_symbol}")
                    try:
                        symbol, exchange_str = vt_symbol.split('.')
                        exchange_obj = Exchange(exchange_str)

                        # 获取数据概览
                        logger.info(f"调用 database_manager.get_bar_overview for {symbol=}, {exchange_obj=}, {interval=}")
                        overview = self.database_manager.get_bar_overview(symbol, exchange_obj, interval)
                        logger.info(f"database_manager.get_bar_overview 调用完成，返回: {overview}")

                        if overview:
                            overviews.append({
                                "symbol": symbol,
                                "exchange": exchange_str,
                                "interval": interval.value,
                                "count": overview.count,
                                "start": overview.start,
                                "end": overview.end
                            })
                        else:
                            logger.warning(f"database_manager.get_bar_overview 返回了 None 或 Falsy 值 for {symbol=}, {exchange_obj=}, {interval=}")
                            
                    except AttributeError as ae:
                        logger.exception(f"处理合约 {vt_symbol} (周期 {interval}) 时发生 AttributeError: {ae}")
                        # 可以选择继续处理下一个合约或直接抛出
                        # raise # 如果希望API调用失败，可以取消注释这行
                    except Exception as ex:
                        logger.exception(f"处理合约 {vt_symbol} (周期 {interval}) 时发生未知错误: {ex}")
                        
            except Exception as e:
                logger.exception(f"获取周期 {interval} 的合约列表时出错: {e}")
                
        logger.info(f"K线数据概览获取完成，共 {len(overviews)} 条.")
        return overviews

    def get_tick_overview(self) -> List[Dict[str, Any]]:
        """获取Tick数据概览

        返回:
            List[Dict[str, Any]]: Tick数据概览列表
        """
        logger.info("开始获取Tick数据概览...")
        overviews = []
        try:
            # 获取所有Tick数据的合约
            symbols = self.database_manager.get_tick_symbols()
            logger.info(f"找到Tick数据合约: {symbols}")

            # 遍历所有合约
            for vt_symbol in symbols:
                logger.info(f"处理Tick合约: {vt_symbol}")
                try:
                    symbol, exchange_str = vt_symbol.split('.')
                    exchange_obj = Exchange(exchange_str)

                    # 获取数据概览
                    logger.info(f"调用 database_manager.get_tick_overview for {symbol=}, {exchange_obj=}")
                    overview = self.database_manager.get_tick_overview(symbol, exchange_obj)
                    logger.info(f"database_manager.get_tick_overview 调用完成，返回: {overview}")

                    if overview:
                        overviews.append({
                            "symbol": symbol,
                            "exchange": exchange_str,
                            "count": overview.count,
                            "start": overview.start,
                            "end": overview.end
                        })
                    else:
                       logger.warning(f"database_manager.get_tick_overview 返回了 None 或 Falsy 值 for {symbol=}, {exchange_obj=}")
                       
                except AttributeError as ae:
                    logger.exception(f"处理Tick合约 {vt_symbol} 时发生 AttributeError: {ae}")
                    # raise
                except Exception as ex:
                    logger.exception(f"处理Tick合约 {vt_symbol} 时发生未知错误: {ex}")
                    
        except Exception as e:
            logger.exception(f"获取Tick合约列表时出错: {e}")
            
        logger.info(f"Tick数据概览获取完成，共 {len(overviews)} 条.")
        return overviews

    # ---- 数据删除功能 ----

    def delete_bar_data(
        self,
        symbol: str,
        exchange: Union[str, Exchange],
        interval: Union[str, Interval]
    ) -> int:
        """删除K线数据

        参数:
            symbol: 代码
            exchange: 交易所
            interval: 周期

        返回:
            int: 删除的数据数量
        """
        # 确保交易所和周期是正确的类型
        if isinstance(exchange, str):
            exchange = Exchange(exchange)

        if isinstance(interval, str):
            interval = Interval(interval)

        # 使用vnpy的数据库管理器删除数据
        count = self.database_manager.delete_bar_data(
            symbol=symbol,
            exchange=exchange,
            interval=interval
        )

        return count

    def delete_tick_data(
        self,
        symbol: str,
        exchange: Union[str, Exchange]
    ) -> int:
        """删除Tick数据

        参数:
            symbol: 代码
            exchange: 交易所

        返回:
            int: 删除的数据数量
        """
        # 确保交易所是正确的类型
        if isinstance(exchange, str):
            exchange = Exchange(exchange)

        # 使用vnpy的数据库管理器删除数据
        count = self.database_manager.delete_tick_data(
            symbol=symbol,
            exchange=exchange
        )

        return count

    # ---- 数据导入导出功能 ----

    def import_bar_data_from_csv(
        self,
        file_path: str,
        symbol: str,
        exchange: Union[str, Exchange],
        interval: Union[str, Interval],
        datetime_format: str = "%Y-%m-%d %H:%M:%S",
        datetime_column: str = "datetime",
        open_column: str = "open",
        high_column: str = "high",
        low_column: str = "low",
        close_column: str = "close",
        volume_column: str = "volume",
        open_interest_column: str = "open_interest"
    ) -> Tuple[bool, str, int]:
        """从CSV导入K线数据

        参数:
            file_path: CSV文件路径
            symbol: 代码
            exchange: 交易所
            interval: 周期
            datetime_format: 时间格式
            datetime_column: 时间列名
            open_column: 开盘价列名
            high_column: 最高价列名
            low_column: 最低价列名
            close_column: 收盘价列名
            volume_column: 成交量列名
            open_interest_column: 持仓量列名

        返回:
            Tuple[bool, str, int]: (成功标志, 消息, 导入数量)
        """
        # 确保交易所和周期是正确的类型
        if isinstance(exchange, str):
            exchange = Exchange(exchange)

        if isinstance(interval, str):
            interval = Interval(interval)

        if not os.path.exists(file_path):
            return False, f"文件不存在: {file_path}", 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                if not reader.fieldnames:
                    return False, "CSV文件格式错误: 没有列名", 0

                # 检查必要的列是否存在
                required_columns = [
                    datetime_column, open_column, high_column,
                    low_column, close_column, volume_column
                ]

                for column in required_columns:
                    if column not in reader.fieldnames:
                        return False, f"CSV文件缺少必要的列: {column}", 0

                # 读取数据
                bars = []
                for row in reader:
                    try:
                        dt = datetime.strptime(row[datetime_column], datetime_format)
                        open_price = float(row[open_column])
                        high_price = float(row[high_column])
                        low_price = float(row[low_column])
                        close_price = float(row[close_column])
                        volume = float(row[volume_column])

                        # 持仓量可能不存在
                        open_interest = 0
                        if open_interest_column in row and row[open_interest_column]:
                            open_interest = float(row[open_interest_column])

                        bar = BarData(
                            symbol=symbol,
                            exchange=exchange,
                            datetime=dt,
                            interval=interval,
                            open_price=open_price,
                            high_price=high_price,
                            low_price=low_price,
                            close_price=close_price,
                            volume=volume,
                            open_interest=open_interest
                        )
                        bars.append(bar)
                    except Exception as e:
                        print(f"解析CSV行出错: {e}, 行: {row}")

                # 保存数据
                count = self.save_bar_data(bars)

                return True, f"成功导入 {count} 条K线数据", count
        except Exception as e:
            return False, f"导入CSV文件出错: {e}", 0

    def export_bar_data_to_csv(
        self,
        file_path: str,
        symbol: str,
        exchange: Union[str, Exchange],
        interval: Union[str, Interval],
        start: datetime,
        end: datetime
    ) -> Tuple[bool, str, int]:
        """导出K线数据到CSV

        参数:
            file_path: CSV文件路径
            symbol: 代码
            exchange: 交易所
            interval: 周期
            start: 开始时间
            end: 结束时间

        返回:
            Tuple[bool, str, int]: (成功标志, 消息, 导出数量)
        """
        try:
            # 加载数据
            bars = self.load_bar_data(symbol, exchange, interval, start, end)

            if not bars:
                return False, "没有符合条件的数据", 0

            # 导出到CSV
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)

                # 写入表头
                writer.writerow([
                    "datetime", "open", "high", "low", "close",
                    "volume", "open_interest"
                ])

                # 写入数据
                for bar in bars:
                    writer.writerow([
                        bar.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        bar.open_price,
                        bar.high_price,
                        bar.low_price,
                        bar.close_price,
                        bar.volume,
                        bar.open_interest
                    ])

            return True, f"成功导出 {len(bars)} 条K线数据到 {file_path}", len(bars)
        except Exception as e:
            return False, f"导出CSV文件出错: {e}", 0

    # ---- 数据下载功能 ----

    def download_bar_data(
        self,
        symbol: str,
        exchange: Union[str, Exchange],
        interval: Union[str, Interval],
        start: datetime,
        end: Optional[datetime] = None,
        callback = None
    ) -> Tuple[bool, str, int]:
        """下载K线数据

        参数:
            symbol: 代码
            exchange: 交易所
            interval: 周期
            start: 开始时间
            end: 结束时间
            callback: 回调函数，用于实际下载数据

        返回:
            Tuple[bool, str, int]: (成功标志, 消息, 下载数量)
        """
        # 确保交易所和周期是正确的类型
        if isinstance(exchange, str):
            exchange = Exchange(exchange)

        if isinstance(interval, str):
            interval = Interval(interval)

        # 如果没有提供结束时间，则使用当前时间
        if end is None:
            end = datetime.now()

        # 如果没有提供回调函数，则返回错误
        if callback is None:
            return False, "没有提供数据下载回调函数", 0

        try:
            # 调用回调函数下载数据
            bars = callback(symbol, exchange, interval, start, end)

            if not bars:
                return False, "下载数据失败或没有数据", 0

            # 保存数据
            count = self.save_bar_data(bars)

            return True, f"成功下载并保存 {count} 条K线数据", count
        except Exception as e:
            return False, f"下载数据出错: {e}", 0


