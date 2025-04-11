"""
SimpleTrade数据管理命令处理器

处理数据管理相关的消息指令。
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from vnpy.trader.constant import Exchange, Interval

class DataCommandProcessor:
    """数据管理命令处理器"""
    
    def __init__(self, engine):
        """初始化"""
        self.engine = engine
        self.commands = {
            "query": self.cmd_query,
            "download": self.cmd_download,
            "import": self.cmd_import,
            "export": self.cmd_export,
            "delete": self.cmd_delete,
            "help": self.cmd_help,
        }
    
    def process(self, command_text: str) -> str:
        """处理命令"""
        # 检查命令前缀
        if not command_text.startswith("/data"):
            return ""
        
        # 解析命令
        parts = command_text.split()
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
        """查询数据命令"""
        if not args:
            # 查询所有可用数据
            data = self.engine.get_available_data()
            if not data:
                return "数据库中没有可用数据。"
            
            result = "可用数据列表:\n"
            for i, item in enumerate(data[:10]):  # 只显示前10条
                if item["type"] == "bar":
                    result += f"{i+1}. {item['symbol']}.{item['exchange']} - {item['interval']} - {item['count']}条 ({item['start']} 至 {item['end']})\n"
                else:
                    result += f"{i+1}. {item['symbol']}.{item['exchange']} - Tick - {item['count']}条 ({item['start']} 至 {item['end']})\n"
            
            if len(data) > 10:
                result += f"... 共 {len(data)} 条记录"
            
            return result
        
        if len(args) < 4:
            return "格式: /data query [类型] [代码] [交易所] [周期] [开始日期] [结束日期(可选)]"
        
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
                bars = self.engine.get_bar_data(
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
                    result += f"{i+1}. {bar.datetime.strftime('%Y-%m-%d %H:%M:%S')}: 开{bar.open_price} 高{bar.high_price} 低{bar.low_price} 收{bar.close_price} 量{bar.volume}\n"
                
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
                ticks = self.engine.get_tick_data(
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
                    result += f"{i+1}. {tick.datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}: 最新{tick.last_price} 买1{tick.bid_price_1}({tick.bid_volume_1}) 卖1{tick.ask_price_1}({tick.ask_volume_1})\n"
                
                if len(ticks) > 5:
                    result += f"... 共 {len(ticks)} 条数据"
                
                return result
            except Exception as e:
                return f"查询出错: {str(e)}"
        
        return f"不支持的数据类型: {data_type}。支持的类型: bar, tick"
    
    def cmd_download(self, args: List[str]) -> str:
        """下载数据命令"""
        if len(args) < 4:
            return "格式: /data download [代码] [交易所] [周期] [开始日期] [结束日期(可选)]"
        
        symbol = args[0]
        exchange = args[1]
        interval = args[2]
        start_date = args[3]
        end_date = None
        if len(args) > 4:
            end_date = args[4]
        
        try:
            # 解析参数
            exchange_obj = Exchange(exchange)
            interval_obj = Interval(interval)
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.now()
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # 下载数据
            success = self.engine.download_bar_data(
                symbol=symbol,
                exchange=exchange_obj,
                interval=interval_obj,
                start=start,
                end=end
            )
            
            if success:
                return f"成功下载 {symbol}.{exchange} 的 {interval} 数据"
            else:
                return f"下载 {symbol}.{exchange} 的 {interval} 数据失败"
        except Exception as e:
            return f"下载出错: {str(e)}"
    
    def cmd_import(self, args: List[str]) -> str:
        """导入数据命令"""
        if len(args) < 12:
            return """格式: /data import [文件路径] [代码] [交易所] [周期] [时间列名] [开盘列名] [最高列名] [最低列名] [收盘列名] [成交量列名] [持仓量列名] [时间格式]
            
例如: /data import /path/to/data.csv AAPL SMART 1d datetime open high low close volume open_interest "%Y-%m-%d %H:%M:%S"
            """
        
        file_path = args[0]
        symbol = args[1]
        exchange = args[2]
        interval = args[3]
        datetime_head = args[4]
        open_head = args[5]
        high_head = args[6]
        low_head = args[7]
        close_head = args[8]
        volume_head = args[9]
        open_interest_head = args[10]
        datetime_format = args[11]
        
        try:
            # 解析参数
            exchange_obj = Exchange(exchange)
            interval_obj = Interval(interval)
            
            # 导入数据
            success, msg = self.engine.import_data_from_csv(
                file_path=file_path,
                symbol=symbol,
                exchange=exchange_obj,
                interval=interval_obj,
                datetime_head=datetime_head,
                open_head=open_head,
                high_head=high_head,
                low_head=low_head,
                close_head=close_head,
                volume_head=volume_head,
                open_interest_head=open_interest_head,
                datetime_format=datetime_format
            )
            
            return msg
        except Exception as e:
            return f"导入出错: {str(e)}"
    
    def cmd_export(self, args: List[str]) -> str:
        """导出数据命令"""
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
            success, msg = self.engine.export_data_to_csv(
                symbol=symbol,
                exchange=exchange_obj,
                interval=interval_obj,
                start=start,
                end=end,
                file_path=file_path
            )
            
            return msg
        except Exception as e:
            return f"导出出错: {str(e)}"
    
    def cmd_delete(self, args: List[str]) -> str:
        """删除数据命令"""
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
                
                success, msg = self.engine.delete_bar_data(
                    symbol=symbol,
                    exchange=exchange_obj,
                    interval=interval_obj
                )
            elif data_type == "tick":
                success, msg = self.engine.delete_tick_data(
                    symbol=symbol,
                    exchange=exchange_obj
                )
            else:
                return f"不支持的数据类型: {data_type}。支持的类型: bar, tick"
            
            return msg
        except Exception as e:
            return f"删除出错: {str(e)}"
    
    def cmd_help(self, args: List[str]) -> str:
        """帮助命令"""
        return """
数据管理命令帮助:

/data query - 查询数据
  /data query - 查询所有可用数据
  /data query bar [代码] [交易所] [周期] [开始日期] [结束日期(可选)] - 查询K线数据
  /data query tick [代码] [交易所] [开始日期] [结束日期(可选)] - 查询Tick数据

/data download [代码] [交易所] [周期] [开始日期] [结束日期(可选)] - 下载数据

/data import [文件路径] [代码] [交易所] [周期] [时间列名] [开盘列名] [最高列名] [最低列名] [收盘列名] [成交量列名] [持仓量列名] [时间格式] - 从CSV导入数据

/data export [代码] [交易所] [周期] [开始日期] [结束日期] [文件路径] - 导出数据到CSV

/data delete [类型] [代码] [交易所] [周期(仅bar类型需要)] - 删除数据

/data help - 显示帮助信息

示例:
/data query bar AAPL SMART 1d 2023-01-01 2023-12-31
/data download AAPL SMART 1d 2023-01-01
/data import /path/to/data.csv AAPL SMART 1d datetime open high low close volume open_interest "%Y-%m-%d %H:%M:%S"
/data export AAPL SMART 1d 2023-01-01 2023-12-31 /path/to/export.csv
/data delete bar AAPL SMART 1d
"""
