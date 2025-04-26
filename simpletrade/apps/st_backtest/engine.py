"""
SimpleTrade回测引擎

提供统一的回测引擎接口，支持不同类型的策略回测
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional

import pandas as pd
from vnpy.trader.constant import Interval, Exchange
from vnpy_ctastrategy.backtesting import BacktestingEngine as CTABacktestingEngine
from vnpy_ctastrategy.backtesting import BacktestingMode

from simpletrade.core.app import STBaseEngine

# 尝试导入其他策略类型的回测引擎
try:
    from vnpy_optionmaster.backtesting import BacktestingEngine as OptionBacktestingEngine
    HAS_OPTION_ENGINE = True
except ImportError:
    HAS_OPTION_ENGINE = False
    logging.warning("vnpy_optionmaster not found. Option strategy backtesting won't be available.")

try:
    from vnpy_spreadtrading.backtesting import BacktestingEngine as SpreadBacktestingEngine
    HAS_SPREAD_ENGINE = True
except ImportError:
    HAS_SPREAD_ENGINE = False
    logging.warning("vnpy_spreadtrading not found. Spread strategy backtesting won't be available.")

try:
    from vnpy_algotrading.backtesting import BacktestingEngine as AlgoBacktestingEngine
    HAS_ALGO_ENGINE = True
except ImportError:
    HAS_ALGO_ENGINE = False
    logging.warning("vnpy_algotrading not found. Algo strategy backtesting won't be available.")

logger = logging.getLogger("simpletrade.apps.st_backtest.engine")

# Helper functions
def _get_vnpy_interval(interval_str: str) -> Optional[Interval]:
    """转换字符串间隔为VnPy Interval枚举"""
    interval_map = {
        "1m": Interval.MINUTE,
        "1h": Interval.HOUR,
        "d": Interval.DAILY,
        "w": Interval.WEEKLY,
    }
    return interval_map.get(interval_str)

def _get_vnpy_exchange(exchange_str: str) -> Optional[Exchange]:
    """转换字符串交易所为VnPy Exchange枚举"""
    try:
        return Exchange(exchange_str.upper()) # 尝试直接转换 (例如 "SHFE")
    except ValueError:
        # 如果需要,添加映射
        logger.warning(f"无法直接将 '{exchange_str}' 转换为Exchange枚举. 返回None.")
        return None

class AbstractBacktestEngine(ABC):
    """抽象回测引擎基类"""
    
    @abstractmethod
    def set_parameters(self, **kwargs) -> None:
        """设置回测参数"""
        pass
    
    @abstractmethod
    def add_strategy(self, strategy_class: Type, strategy_params: Dict[str, Any]) -> None:
        """添加策略"""
        pass
    
    @abstractmethod
    def load_data(self) -> None:
        """加载历史数据"""
        pass
    
    @abstractmethod
    def run_backtesting(self) -> None:
        """运行回测"""
        pass
    
    @abstractmethod
    def calculate_result(self) -> None:
        """计算回测结果"""
        pass
    
    @abstractmethod
    def calculate_statistics(self) -> Dict[str, Any]:
        """计算回测统计指标"""
        pass
    
    @abstractmethod
    def get_daily_results(self) -> pd.DataFrame:
        """获取每日结果"""
        pass
    
    @abstractmethod
    def get_all_trades(self) -> List[Any]:
        """获取所有交易记录"""
        pass
    
    @property
    @abstractmethod
    def history_data(self) -> List[Any]:
        """获取历史数据"""
        pass


class CTABacktestEngine(AbstractBacktestEngine):
    """CTA策略回测引擎"""
    
    def __init__(self):
        """初始化"""
        self.engine = CTABacktestingEngine()
        
    def set_parameters(self, **kwargs) -> None:
        """设置回测参数"""
        self.engine.set_parameters(**kwargs)
    
    def add_strategy(self, strategy_class: Type, strategy_params: Dict[str, Any]) -> None:
        """添加策略"""
        self.engine.add_strategy(strategy_class, strategy_params)
    
    def load_data(self) -> None:
        """加载历史数据"""
        self.engine.load_data()
    
    def run_backtesting(self) -> None:
        """运行回测"""
        self.engine.run_backtesting()
    
    def calculate_result(self) -> None:
        """计算回测结果"""
        self.engine.calculate_result()
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """计算回测统计指标"""
        return self.engine.calculate_statistics()
    
    def get_daily_results(self) -> pd.DataFrame:
        """获取每日结果"""
        return pd.DataFrame(self.engine.get_daily_results()).fillna(0.0)
    
    def get_all_trades(self) -> List[Any]:
        """获取所有交易记录"""
        return self.engine.get_all_trades()
    
    @property
    def history_data(self) -> List[Any]:
        """获取历史数据"""
        return self.engine.history_data


# 如果支持期权策略，添加期权回测引擎
if HAS_OPTION_ENGINE:
    class OptionBacktestEngine(AbstractBacktestEngine):
        """期权策略回测引擎"""
        
        def __init__(self):
            """初始化"""
            self.engine = OptionBacktestingEngine()
            
        def set_parameters(self, **kwargs) -> None:
            """设置回测参数"""
            self.engine.set_parameters(**kwargs)
        
        def add_strategy(self, strategy_class: Type, strategy_params: Dict[str, Any]) -> None:
            """添加策略"""
            self.engine.add_strategy(strategy_class, strategy_params)
        
        def load_data(self) -> None:
            """加载历史数据"""
            self.engine.load_data()
        
        def run_backtesting(self) -> None:
            """运行回测"""
            self.engine.run_backtesting()
        
        def calculate_result(self) -> None:
            """计算回测结果"""
            self.engine.calculate_result()
        
        def calculate_statistics(self) -> Dict[str, Any]:
            """计算回测统计指标"""
            return self.engine.calculate_statistics()
        
        def get_daily_results(self) -> pd.DataFrame:
            """获取每日结果"""
            return pd.DataFrame(self.engine.get_daily_results()).fillna(0.0)
        
        def get_all_trades(self) -> List[Any]:
            """获取所有交易记录"""
            return self.engine.get_all_trades()
        
        @property
        def history_data(self) -> List[Any]:
            """获取历史数据"""
            return self.engine.history_data


class BacktestEngineFactory:
    """回测引擎工厂，根据策略类型创建合适的回测引擎"""
    
    @staticmethod
    def create_engine(strategy_type: str) -> AbstractBacktestEngine:
        """
        创建回测引擎
        
        Args:
            strategy_type (str): 策略类型，如 'cta', 'option', 'spread', 'algo'
            
        Returns:
            AbstractBacktestEngine: 回测引擎实例
            
        Raises:
            ValueError: 如果策略类型不支持
        """
        if strategy_type is None:
            logger.warning("策略类型为None，使用默认的CTA回测引擎")
            return CTABacktestEngine()
            
        strategy_type = strategy_type.lower()
        
        if strategy_type in ['cta', 'cat']:  # 添加对'cat'类型的支持
            return CTABacktestEngine()
        elif strategy_type == 'option' and HAS_OPTION_ENGINE:
            return OptionBacktestEngine()
        # 添加其他策略类型...
        else:
            # 默认使用CTA回测引擎
            logger.warning(f"策略类型 '{strategy_type}' 不支持或未找到对应回测引擎, 使用默认的CTA回测引擎")
            return CTABacktestEngine()


class STBacktestEngine(STBaseEngine):
    """SimpleTrade回测引擎"""
    
    def __init__(self, main_engine=None, event_engine=None, app_name=None):
        """初始化回测引擎"""
        super().__init__(main_engine, event_engine, app_name)
        self.factory = BacktestEngineFactory()
        
    def create_backtest_engine(self, strategy_type: str) -> AbstractBacktestEngine:
        """创建回测引擎实例"""
        return self.factory.create_engine(strategy_type) 