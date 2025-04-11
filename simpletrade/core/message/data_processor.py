"""
SimpleTrade数据管理消息处理器

处理数据管理相关的消息指令。
直接使用vnpy的数据模型和数据管理功能。
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# 导入vnpy的数据模型和数据管理功能
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval

# 导入我们的数据管理器
from simpletrade.core.data import DataManager
from .processor import CommandProcessor


class DataCommandProcessor(CommandProcessor):
    """数据管理命令处理器"""

    def __init__(self, data_manager: DataManager):
        """初始化

        参数:
            data_manager: 数据管理器
        """
        super().__init__("/data")
        self.data_manager = data_manager
        self.commands = {
            "query": self.cmd_query,
            "import": self.cmd_import,
            "export": self.cmd_export,
            "delete": self.cmd_delete,
            "help": self.cmd_help,
        }

    def process(self, command: str) -> str:
        """处理命令

        参数:
            command: 命令文本

        返回:
            str: 处理结果
        """
        # 解析命令
        parts = command.split()
        if len(parts) < 2:
            return "无效的命令格式。使用 `/data help` 获取帮助。"

        cmd = parts[1].lower()
        args = parts[2:]

        # 执行命令
        if cmd in self.commands:
            try:
                return self.commands[cmd](args)
            except Exception as e:
                return f"命令执行错误: {str(e)}"
        else:
            return f"未知命令: {cmd}。使用 `/data help` 获取帮助。"

    def cmd_query(self, args: List[str]) -> str:
        """查询数据命令

        参数:
            args: 命令参数

        返回:
            str: 处理结果
        """
        if not args:
            # 查询所有可用数据
            bar_overviews = self.data_manager.get_bar_overview()
            tick_overviews = self.data_manager.get_tick_overview()

            if not bar_overviews and not tick_overviews:
                return "数据库中没有可用数据。"

            result = "可用数据列表:\n"

            # 显示K线数据
            for i, overview in enumerate(bar_overviews):
                result += f"{i+1}. {overview.symbol}.{overview.exchange.value} - {overview.interval.value} - {overview.count}条 ({overview.start.strftime('%Y-%m-%d')} 至 {overview.end.strftime('%Y-%m-%d')})\n"

            # 显示Tick数据
            for i, overview in enumerate(tick_overviews, start=len(bar_overviews)+1):
                result += f"{i}. {overview.symbol}.{overview.exchange.value} - Tick - {overview.count}条 ({overview.start.strftime('%Y-%m-%d')} 至 {overview.end.strftime('%Y-%m-%d')})\n"

            return result

        if len(args) < 4:
            return "格式: /data query [类型] [代码] [交易所] [周期(仅bar类型需要)] [开始日期] [结束日期(可选)]"

        data_type = args[0]  # bar 或 tick
        symbol = args[1]
        exchange = args[2]

        if data_type == "bar":
            if len(args) < 5:
                return "格式: /data query bar [代码] [交易所] [周期] [开始日期] [结束日期(可选)]"

            interval = args[3]
            start_date = args[4]
            end_date = None
            if len(args) > 5:
                end_date = args[5]

            try:
                # 解析参数
                exchange_obj = Exchange(exchange)
                interval_obj = Interval(interval)
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.now()
                if end_date:
                    end = datetime.strptime(end_date, "%Y-%m-%d")

                # 查询数据
                bars = self.data_manager.load_bar_data(
                    symbol=symbol,
                    exchange=exchange_obj,
                    interval=interval_obj,
                    start=start,
                    end=end
                )

                if not bars:
                    return "未找到符合条件的数据"

                # 格式化输出
                result = f"查询到 {len(bars)} 条K线数据:\n"
                for i, bar in enumerate(bars[:5]):  # 只显示前5条
                    result += f"{i+1}. {bar.datetime.strftime('%Y-%m-%d %H:%M:%S')}: 开{bar.open_price:.2f} 高{bar.high_price:.2f} 低{bar.low_price:.2f} 收{bar.close_price:.2f} 量{bar.volume:.2f}\n"

                if len(bars) > 5:
                    result += f"... 共 {len(bars)} 条数据"

                return result
            except Exception as e:
                return f"查询出错: {str(e)}"

        elif data_type == "tick":
            if len(args) < 4:
                return "格式: /data query tick [代码] [交易所] [开始日期] [结束日期(可选)]"

            start_date = args[3]
            end_date = None
            if len(args) > 4:
                end_date = args[4]

            try:
                # 解析参数
                exchange_obj = Exchange(exchange)
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.now()
                if end_date:
                    end = datetime.strptime(end_date, "%Y-%m-%d")

                # 查询数据
                ticks = self.data_manager.load_tick_data(
                    symbol=symbol,
                    exchange=exchange_obj,
                    start=start,
                    end=end
                )

                if not ticks:
                    return "未找到符合条件的数据"

                # 格式化输出
                result = f"查询到 {len(ticks)} 条Tick数据:\n"
                for i, tick in enumerate(ticks[:5]):  # 只显示前5条
                    result += f"{i+1}. {tick.datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}: 最新{tick.last_price:.2f} 买1{tick.bid_price_1:.2f}({tick.bid_volume_1:.2f}) 卖1{tick.ask_price_1:.2f}({tick.ask_volume_1:.2f})\n"

                if len(ticks) > 5:
                    result += f"... 共 {len(ticks)} 条数据"

                return result
            except Exception as e:
                return f"查询出错: {str(e)}"

        return f"不支持的数据类型: {data_type}。支持的类型: bar, tick"

    def cmd_import(self, args: List[str]) -> str:
        """导入数据命令

        参数:
            args: 命令参数

        返回:
            str: 处理结果
        """
        if len(args) < 4:
            return """格式: /data import [文件路径] [代码] [交易所] [周期]

可选参数:
--datetime-format [格式]  # 默认: %Y-%m-%d %H:%M:%S
--datetime-column [列名]  # 默认: datetime
--open-column [列名]      # 默认: open
--high-column [列名]      # 默认: high
--low-column [列名]       # 默认: low
--close-column [列名]     # 默认: close
--volume-column [列名]    # 默认: volume
--oi-column [列名]        # 默认: open_interest

例如: /data import /path/to/data.csv AAPL NASDAQ 1d --datetime-format "%Y-%m-%d"
            """

        file_path = args[0]
        symbol = args[1]
        exchange = args[2]
        interval = args[3]

        # 解析可选参数
        kwargs = {}
        i = 4
        while i < len(args):
            if args[i].startswith("--"):
                param = args[i][2:].replace("-", "_")
                if i + 1 < len(args) and not args[i + 1].startswith("--"):
                    kwargs[param] = args[i + 1]
                    i += 2
                else:
                    kwargs[param] = True
                    i += 1
            else:
                i += 1

        # 映射参数名
        param_mapping = {
            "datetime_format": "datetime_format",
            "datetime_column": "datetime_column",
            "open_column": "open_column",
            "high_column": "high_column",
            "low_column": "low_column",
            "close_column": "close_column",
            "volume_column": "volume_column",
            "oi_column": "open_interest_column"
        }

        # 转换参数名
        import_kwargs = {}
        for key, value in kwargs.items():
            if key in param_mapping:
                import_kwargs[param_mapping[key]] = value

        try:
            # 导入数据
            success, msg, count = self.data_manager.import_bar_data_from_csv(
                file_path=file_path,
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                **import_kwargs
            )

            return msg
        except Exception as e:
            return f"导入出错: {str(e)}"

    def cmd_export(self, args: List[str]) -> str:
        """导出数据命令

        参数:
            args: 命令参数

        返回:
            str: 处理结果
        """
        if len(args) < 6:
            return "格式: /data export [代码] [交易所] [周期] [开始日期] [结束日期] [文件路径]"

        symbol = args[0]
        exchange = args[1]
        interval = args[2]
        start_date = args[3]
        end_date = args[4]
        file_path = args[5]

        try:
            # 解析参数
            exchange_obj = Exchange(exchange)
            interval_obj = Interval(interval)
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            # 导出数据
            success, msg, count = self.data_manager.export_bar_data_to_csv(
                file_path=file_path,
                symbol=symbol,
                exchange=exchange_obj,
                interval=interval_obj,
                start=start,
                end=end
            )

            return msg
        except Exception as e:
            return f"导出出错: {str(e)}"

    def cmd_delete(self, args: List[str]) -> str:
        """删除数据命令

        参数:
            args: 命令参数

        返回:
            str: 处理结果
        """
        if len(args) < 3:
            return "格式: /data delete [类型] [代码] [交易所] [周期(仅bar类型需要)]"

        data_type = args[0]  # bar 或 tick
        symbol = args[1]
        exchange = args[2]

        try:
            # 解析参数
            exchange_obj = Exchange(exchange)

            # 删除数据
            if data_type == "bar":
                if len(args) < 4:
                    return "格式: /data delete bar [代码] [交易所] [周期]"

                interval = args[3]
                interval_obj = Interval(interval)

                count = self.data_manager.delete_bar_data(
                    symbol=symbol,
                    exchange=exchange_obj,
                    interval=interval_obj
                )

                return f"成功删除 {count} 条K线数据"
            elif data_type == "tick":
                count = self.data_manager.delete_tick_data(
                    symbol=symbol,
                    exchange=exchange_obj
                )

                return f"成功删除 {count} 条Tick数据"
            else:
                return f"不支持的数据类型: {data_type}。支持的类型: bar, tick"
        except Exception as e:
            return f"删除出错: {str(e)}"

    def cmd_help(self, args: List[str]) -> str:
        """帮助命令

        参数:
            args: 命令参数

        返回:
            str: 处理结果
        """
        return """
数据管理命令帮助:

/data query - 查询数据
  /data query - 查询所有可用数据
  /data query bar [代码] [交易所] [周期] [开始日期] [结束日期(可选)] - 查询K线数据
  /data query tick [代码] [交易所] [开始日期] [结束日期(可选)] - 查询Tick数据

/data import [文件路径] [代码] [交易所] [周期] - 从CSV导入数据
  可选参数:
  --datetime-format [格式]  # 默认: %Y-%m-%d %H:%M:%S
  --datetime-column [列名]  # 默认: datetime
  --open-column [列名]      # 默认: open
  --high-column [列名]      # 默认: high
  --low-column [列名]       # 默认: low
  --close-column [列名]     # 默认: close
  --volume-column [列名]    # 默认: volume
  --oi-column [列名]        # 默认: open_interest

/data export [代码] [交易所] [周期] [开始日期] [结束日期] [文件路径] - 导出数据到CSV

/data delete [类型] [代码] [交易所] [周期(仅bar类型需要)] - 删除数据

/data help - 显示帮助信息

示例:
/data query bar AAPL NASDAQ 1d 2023-01-01 2023-12-31
/data import /path/to/data.csv AAPL NASDAQ 1d --datetime-format "%Y-%m-%d"
/data export AAPL NASDAQ 1d 2023-01-01 2023-12-31 /path/to/export.csv
/data delete bar AAPL NASDAQ 1d
"""
