"""
SimpleTrade分析应用命令处理器
"""

from typing import List, Dict, Any
from datetime import datetime

from vnpy.trader.constant import Exchange, Interval

class AnalysisCommandProcessor:
    """分析命令处理器"""
    
    def __init__(self, engine):
        """初始化"""
        self.engine = engine
        self.commands = {
            "indicator": self.cmd_indicator,
            "backtest": self.cmd_backtest,
            "help": self.cmd_help,
        }
    
    def process(self, command_text: str) -> str:
        """处理命令"""
        # 检查命令前缀
        if not command_text.startswith("/analysis"):
            return ""
        
        # 解析命令
        parts = command_text.split()
        if len(parts) < 2:
            return "无效的命令格式。使用 `/analysis help` 获取帮助。"
        
        cmd = parts[1].lower()
        args = parts[2:]
        
        # 执行命令
        if cmd in self.commands:
            try:
                return self.commands[cmd](args)
            except Exception as e:
                return f"命令执行错误: {str(e)}"
        else:
            return f"未知命令: {cmd}。使用 `/analysis help` 获取帮助。"
    
    def cmd_indicator(self, args: List[str]) -> str:
        """计算技术指标命令"""
        if len(args) < 5:
            return "格式: /analysis indicator [代码] [交易所] [周期] [开始日期] [结束日期] [指标1] [指标2] ..."
        
        symbol = args[0]
        exchange = args[1]
        interval = args[2]
        start_date = args[3]
        end_date = args[4]
        indicators = args[5:]
        
        if not indicators:
            indicators = ["ma", "macd", "rsi"]  # 默认指标
        
        try:
            # 解析参数
            exchange_obj = Exchange(exchange)
            interval_obj = Interval(interval)
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # 获取数据
            data_engine = self.engine.main_engine.get_engine("st_datamanager")
            if not data_engine:
                return "错误：无法获取数据管理引擎"
            
            bars = data_engine.get_bar_data(
                symbol=symbol,
                exchange=exchange_obj,
                interval=interval_obj,
                start=start,
                end=end
            )
            
            if not bars:
                return "未找到符合条件的数据"
            
            # 计算指标
            df = self.engine.calculate_indicators(bars, indicators)
            
            # 格式化输出
            result = f"计算 {symbol}.{exchange} 的技术指标:\n"
            for indicator in indicators:
                if indicator == "ma":
                    result += "- 移动平均线 (MA5, MA10, MA20, MA60)\n"
                elif indicator == "macd":
                    result += "- MACD (12, 26, 9)\n"
                elif indicator == "rsi":
                    result += "- RSI (14)\n"
            
            result += f"\n最近数据 ({df.index[-1].strftime('%Y-%m-%d')}):\n"
            
            # 显示最近的指标值
            last_row = df.iloc[-1]
            if "ma5" in df.columns:
                result += f"MA5: {last_row['ma5']:.2f}, MA10: {last_row['ma10']:.2f}, MA20: {last_row['ma20']:.2f}\n"
            if "macd" in df.columns:
                result += f"MACD: {last_row['macd']:.4f}, Signal: {last_row['macd_signal']:.4f}, Hist: {last_row['macd_hist']:.4f}\n"
            if "rsi" in df.columns:
                result += f"RSI: {last_row['rsi']:.2f}\n"
            
            return result
        except Exception as e:
            return f"计算指标出错: {str(e)}"
    
    def cmd_backtest(self, args: List[str]) -> str:
        """回测策略命令"""
        if len(args) < 5:
            return "格式: /analysis backtest [代码] [交易所] [周期] [开始日期] [结束日期] [策略参数]"
        
        symbol = args[0]
        exchange = args[1]
        interval = args[2]
        start_date = args[3]
        end_date = args[4]
        
        # 解析策略参数（简化版，实际应用中可能需要更复杂的解析）
        strategy_params = {
            "ma_cross": {
                "fast": 5,
                "slow": 20
            }
        }
        
        try:
            # 解析参数
            exchange_obj = Exchange(exchange)
            interval_obj = Interval(interval)
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # 获取数据
            data_engine = self.engine.main_engine.get_engine("st_datamanager")
            if not data_engine:
                return "错误：无法获取数据管理引擎"
            
            bars = data_engine.get_bar_data(
                symbol=symbol,
                exchange=exchange_obj,
                interval=interval_obj,
                start=start,
                end=end
            )
            
            if not bars:
                return "未找到符合条件的数据"
            
            # 回测策略
            results = self.engine.backtest_strategy(bars, strategy_params)
            
            # 格式化输出
            result = f"回测 {symbol}.{exchange} 的策略结果:\n"
            result += f"策略: MA交叉 (快线: {strategy_params['ma_cross']['fast']}, 慢线: {strategy_params['ma_cross']['slow']})\n"
            result += f"时间段: {start_date} 至 {end_date}\n\n"
            
            result += f"年化收益率: {results['annual_return']:.2%}\n"
            result += f"最大回撤: {results['max_drawdown']:.2%}\n"
            result += f"夏普比率: {results['sharpe_ratio']:.2f}\n"
            result += f"总收益率: {results['total_return']:.2%}\n"
            result += f"胜率: {results['win_rate']:.2%}\n"
            
            return result
        except Exception as e:
            return f"回测出错: {str(e)}"
    
    def cmd_help(self, args: List[str]) -> str:
        """帮助命令"""
        return """
分析命令帮助:

/analysis indicator [代码] [交易所] [周期] [开始日期] [结束日期] [指标1] [指标2] ... - 计算技术指标
  支持的指标: ma, macd, rsi

/analysis backtest [代码] [交易所] [周期] [开始日期] [结束日期] [策略参数] - 回测策略
  目前支持的策略: MA交叉

/analysis help - 显示帮助信息

示例:
/analysis indicator AAPL SMART 1d 2023-01-01 2023-12-31 ma macd
/analysis backtest AAPL SMART 1d 2023-01-01 2023-12-31
"""
