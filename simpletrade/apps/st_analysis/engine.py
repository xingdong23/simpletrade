"""
SimpleTrade分析引擎

提供数据分析功能，包括技术指标计算、策略回测和可视化分析。
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
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from vnpy.trader.object import BarData
from vnpy.trader.constant import Interval, Exchange

from simpletrade.core.app import STBaseEngine

class STAnalysisEngine(STBaseEngine):
    """SimpleTrade分析引擎"""

    def __init__(self, main_engine, event_engine, engine_name: str):
        """初始化"""
        super().__init__(main_engine, event_engine, engine_name)

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
            import sys
            sys.modules["simpletrade.apps.st_analysis.api.engine"] = self
        except Exception as e:
            self.write_log(f"API路由初始化失败：{str(e)}")

    def init_message_commands(self):
        """初始化消息指令"""
        try:
            from .commands import AnalysisCommandProcessor
            self.command_processor = AnalysisCommandProcessor(self)
            self.write_log("消息指令处理器初始化成功")

            # 将指令处理器注册到消息引擎（如果存在）
            message_engine = self.main_engine.get_engine("st_message")
            if message_engine:
                message_engine.register_processor("/analysis", self.command_processor)
                self.write_log("消息指令处理器注册成功")
            else:
                self.write_log("警告：st_message引擎未找到，消息指令将无法使用")
        except Exception as e:
            self.write_log(f"消息指令处理器初始化失败：{str(e)}")

    def write_log(self, msg: str):
        """写入日志"""
        self.main_engine.write_log(msg, source=self.engine_name)

    # ---- 从core/analysis移动过来的功能 ----

    def calculate_indicators(self, bars: List[BarData], indicators: List[str]) -> pd.DataFrame:
        """计算技术指标"""
        # 将K线数据转换为DataFrame
        df = self.bars_to_dataframe(bars)
        
        # 计算指标
        for indicator in indicators:
            if indicator == "ma":
                df = self.calculate_ma(df)
            elif indicator == "macd":
                df = self.calculate_macd(df)
            elif indicator == "rsi":
                df = self.calculate_rsi(df)
            # 可以添加更多指标...
        
        return df

    def bars_to_dataframe(self, bars: List[BarData]) -> pd.DataFrame:
        """将K线数据转换为DataFrame"""
        data = []
        for bar in bars:
            data.append({
                "datetime": bar.datetime,
                "open": bar.open_price,
                "high": bar.high_price,
                "low": bar.low_price,
                "close": bar.close_price,
                "volume": bar.volume,
                "open_interest": bar.open_interest
            })
        
        df = pd.DataFrame(data)
        df.set_index("datetime", inplace=True)
        return df

    def calculate_ma(self, df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """计算移动平均线"""
        for period in periods:
            df[f"ma{period}"] = df["close"].rolling(period).mean()
        return df

    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """计算MACD指标"""
        # 计算EMA
        ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
        ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
        
        # 计算MACD线和信号线
        df["macd"] = ema_fast - ema_slow
        df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]
        
        return df

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """计算RSI指标"""
        # 计算价格变化
        delta = df["close"].diff()
        
        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 计算平均上涨和下跌
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # 计算相对强度和RSI
        rs = avg_gain / avg_loss
        df["rsi"] = 100 - (100 / (1 + rs))
        
        return df

    def backtest_strategy(self, bars: List[BarData], strategy_params: Dict[str, Any]) -> Dict[str, Any]:
        """回测策略"""
        # 将K线数据转换为DataFrame
        df = self.bars_to_dataframe(bars)
        
        # 根据策略参数计算指标
        if "ma" in strategy_params:
            df = self.calculate_ma(df, strategy_params["ma"])
        if "macd" in strategy_params:
            df = self.calculate_macd(df, **strategy_params["macd"])
        if "rsi" in strategy_params:
            df = self.calculate_rsi(df, strategy_params["rsi"])
        
        # 生成交易信号
        df = self.generate_signals(df, strategy_params)
        
        # 计算回测结果
        results = self.calculate_returns(df)
        
        return results

    def generate_signals(self, df: pd.DataFrame, strategy_params: Dict[str, Any]) -> pd.DataFrame:
        """生成交易信号"""
        # 这里是一个简单的示例，实际应用中需要根据具体策略生成信号
        df["signal"] = 0
        
        if "ma_cross" in strategy_params:
            fast = strategy_params["ma_cross"]["fast"]
            slow = strategy_params["ma_cross"]["slow"]
            
            # 计算快线和慢线
            if f"ma{fast}" not in df.columns:
                df = self.calculate_ma(df, [fast])
            if f"ma{slow}" not in df.columns:
                df = self.calculate_ma(df, [slow])
            
            # 生成信号：快线上穿慢线买入，下穿卖出
            df["signal"] = np.where(df[f"ma{fast}"] > df[f"ma{slow}"], 1, 0)
            df["signal"] = np.where(df[f"ma{fast}"] < df[f"ma{slow}"], -1, df["signal"])
        
        return df

    def calculate_returns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算回测结果"""
        # 计算每日收益率
        df["returns"] = df["close"].pct_change()
        
        # 计算策略收益率
        df["strategy_returns"] = df["signal"].shift(1) * df["returns"]
        
        # 计算累计收益率
        df["cumulative_returns"] = (1 + df["returns"]).cumprod() - 1
        df["strategy_cumulative_returns"] = (1 + df["strategy_returns"]).cumprod() - 1
        
        # 计算最大回撤
        df["peak"] = df["strategy_cumulative_returns"].cummax()
        df["drawdown"] = (df["strategy_cumulative_returns"] - df["peak"]) / (1 + df["peak"])
        max_drawdown = df["drawdown"].min()
        
        # 计算年化收益率
        days = (df.index[-1] - df.index[0]).days
        annual_return = (1 + df["strategy_cumulative_returns"].iloc[-1]) ** (365 / days) - 1
        
        # 计算夏普比率
        sharpe_ratio = df["strategy_returns"].mean() / df["strategy_returns"].std() * (252 ** 0.5)
        
        # 返回结果
        results = {
            "annual_return": annual_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "total_return": df["strategy_cumulative_returns"].iloc[-1],
            "win_rate": len(df[df["strategy_returns"] > 0]) / len(df[df["strategy_returns"] != 0]),
            "data": df
        }
        
        return results

    def visualize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """可视化回测结果"""
        # 在实际应用中，这里可以生成图表或报告
        # 这里只返回一些关键指标
        return {
            "annual_return": results["annual_return"],
            "max_drawdown": results["max_drawdown"],
            "sharpe_ratio": results["sharpe_ratio"],
            "total_return": results["total_return"],
            "win_rate": results["win_rate"]
        }
