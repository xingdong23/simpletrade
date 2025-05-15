"""
SimpleTrade回测引擎

提供统一的回测引擎接口，支持不同类型的策略回测
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional

# 添加vnpy源码路径
import sys
from pathlib import Path

# 添加vnpy源码目录到Python路径
VNPY_CUSTOM_DIR = Path(__file__).parent.parent.parent.parent / "vnpy_custom"
if VNPY_CUSTOM_DIR.exists() and str(VNPY_CUSTOM_DIR) not in sys.path:
    sys.path.insert(0, str(VNPY_CUSTOM_DIR))

import pandas as pd
from vnpy.trader.constant import Interval, Exchange
from vnpy.app.cta_strategy.backtesting import BacktestingEngine as CTABacktestingEngine

from simpletrade.core.app import STBaseEngine

# 尝试导入其他策略类型的回测引擎
try:
    from vnpy.app.option_master.backtesting import BacktestingEngine as OptionBacktestingEngine
    HAS_OPTION_ENGINE = True
except ImportError:
    HAS_OPTION_ENGINE = False
    logging.warning("vnpy.app.option_master not found. Option strategy backtesting won't be available.")

logger = logging.getLogger("simpletrade.apps.st_backtest.engine")

# Helper functions
def _get_vnpy_interval(interval_str: str) -> Optional[Interval]:
    """转换字符串间隔为VnPy Interval枚举"""
    interval_map = {
        "1m": Interval.MINUTE,
        "1h": Interval.HOUR,
        "d": Interval.DAILY,    # 保留 "d" 以防其他地方使用
        "1d": Interval.DAILY,   # 新增 "1d" 映射到日线
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
        # 直接使用vnpy的原生方法
        try:
            # 尝试使用原生方法
            self.engine.add_strategy(strategy_class, strategy_params)
        except TypeError as e:
            # 如果出现类型错误，可能是参数不匹配
            import logging
            logger = logging.getLogger("simpletrade.apps.st_backtest.engine")
            logger.warning(f"使用原生方法添加策略失败: {e}")

            # 尝试手动创建策略实例
            try:
                # 假设策略类需要3个参数（包括self）
                self.engine.strategy = strategy_class(
                    self.engine,
                    strategy_class.__name__,
                    strategy_params
                )
                logger.info(f"成功手动创建策略实例: {strategy_class.__name__}")
            except Exception as e2:
                # 如果仍然失败，抛出异常
                logger.error(f"手动创建策略实例失败: {e2}")
                raise

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
        # 在vnpy的BacktestingEngine类中，calculate_statistics()方法是一个空方法
        # 返回一个空字典作为替代
        stats = self.engine.calculate_statistics()
        if stats is None:
            return {}
        return stats

    def get_daily_results(self) -> pd.DataFrame:
        """获取每日结果"""
        # 在vnpy的BacktestingEngine类中，get_daily_results()方法可能不存在或者返回None
        try:
            daily_results = self.engine.get_daily_results()
            if daily_results is None:
                return pd.DataFrame()
            return pd.DataFrame(daily_results).fillna(0.0)
        except AttributeError:
            # 如果方法不存在，返回空DataFrame
            return pd.DataFrame()
        except Exception as e:
            import logging
            logger = logging.getLogger("simpletrade.apps.st_backtest.engine")
            logger.warning(f"获取每日结果时出错: {e}")
            return pd.DataFrame()

    def get_all_trades(self) -> List[Any]:
        """获取所有交易记录"""
        # 在vnpy的BacktestingEngine类中，get_all_trades()方法可能不存在或者返回None
        try:
            trades = self.engine.get_all_trades()
            if trades is None:
                return []
            return trades
        except AttributeError:
            # 如果方法不存在，返回空列表
            return []
        except Exception as e:
            import logging
            logger = logging.getLogger("simpletrade.apps.st_backtest.engine")
            logger.warning(f"获取交易记录时出错: {e}")
            return []

    @property
    def history_data(self) -> List[Any]:
        """获取历史数据"""
        # 在vnpy的BacktestingEngine类中没有history_data属性
        # 返回一个空列表作为替代
        return getattr(self.engine, "history_data", [])


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