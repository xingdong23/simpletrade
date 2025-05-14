"""
SimpleTrade回测服务

提供策略回测服务功能。
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
import logging
import traceback
import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple

import pandas as pd
import numpy as np

from vnpy.app.cta_strategy.backtesting import BacktestingMode

from simpletrade.config.database import SessionLocal
from simpletrade.models.database import Strategy, BacktestRecord
from simpletrade.strategies import get_strategy_class
from simpletrade.api.schemas.backtest_report import (
    BacktestReportConfigModel,
    EquityCurvePointModel,
    TradeDetailOutputModel,
    BacktestReportDataModel
)
from .engine import BacktestEngineFactory, _get_vnpy_interval, _get_vnpy_exchange

logger = logging.getLogger("simpletrade.apps.st_backtest.service")

class BacktestService:
    """回测服务类"""

    def __init__(self, backtest_engine=None):
        """初始化回测服务

        Args:
            backtest_engine: 回测引擎实例，如果不提供则使用工厂创建
        """
        self.backtest_engine = backtest_engine
        self.backtest_engine_factory = BacktestEngineFactory()

    def _prepare_date_range(self, start_date, end_date) -> Tuple[datetime, datetime]:
        """处理并标准化日期范围

        Args:
            start_date: 开始日期 (可以是日期对象或字符串)
            end_date: 结束日期 (可以是日期对象或字符串)

        Returns:
            tuple: (开始日期, 结束日期) 的datetime对象元组
        """
        # 转换开始日期
        if hasattr(start_date, 'isoformat'):
            start_date_str = start_date.isoformat()
        else:
            start_date_str = str(start_date)

        # 转换结束日期
        if hasattr(end_date, 'isoformat'):
            end_date_str = end_date.isoformat()
        else:
            end_date_str = str(end_date)

        # 转换为datetime对象
        start = datetime.strptime(start_date_str, "%Y-%m-%d")
        end = datetime.strptime(end_date_str, "%Y-%m-%d")

        return start, end

    def _prepare_parameters(self, default_params, user_params) -> Dict[str, Any]:
        """合并并处理策略参数

        Args:
            default_params: 默认参数字典
            user_params: 用户提供的参数字典

        Returns:
            dict: 处理后的最终参数字典
        """
        final_params = {}

        # 从默认参数中提取参数值
        for key, value in default_params.items():
            if isinstance(value, dict) and "default" in value:
                final_params[key] = value["default"]
            else:
                final_params[key] = value

        # 添加用户提供的参数
        if user_params:
            final_params.update(user_params)

        # 处理字符串类型的数值参数
        for key, value in final_params.items():
            if isinstance(value, str):
                if value.replace('.', '', 1).isdigit():  # 更好的数字检测
                    if '.' in value:
                        final_params[key] = float(value)
                    else:
                        final_params[key] = int(value)

        return final_params

    def _process_daily_results(self, engine) -> pd.DataFrame:
        """处理回测每日结果

        Args:
            engine: 回测引擎实例

        Returns:
            pd.DataFrame: 处理后的每日结果DataFrame
        """
        daily_df = pd.DataFrame()

        try:
            # 首先尝试调用get_daily_results()方法
            daily_df = engine.get_daily_results()

            # 如果不是DataFrame，尝试转换
            if not isinstance(daily_df, pd.DataFrame):
                daily_df = pd.DataFrame(daily_df) if daily_df else pd.DataFrame()

            # 转换数据类型
            if not daily_df.empty:
                for col in daily_df.columns:
                    if col != "date":
                        try:
                            daily_df[col] = pd.to_numeric(daily_df[col], errors='coerce')
                        except Exception as e:
                            logger.warning(f"转换列 {col} 为数字类型时出错: {str(e)}")
                            daily_df[col] = None
        except AttributeError:
            # 尝试从不同属性获取每日结果
            if hasattr(engine, 'daily_df'):
                daily_df = engine.daily_df
                if not isinstance(daily_df, pd.DataFrame):
                    daily_df = pd.DataFrame(daily_df) if daily_df else pd.DataFrame()
            elif hasattr(engine, 'engine') and hasattr(engine.engine, 'daily_df'):
                daily_df = engine.engine.daily_df
                if not isinstance(daily_df, pd.DataFrame):
                    daily_df = pd.DataFrame(daily_df) if daily_df else pd.DataFrame()
            else:
                logger.warning("回测引擎没有get_daily_results()方法或daily_df属性")
        except Exception as e:
            logger.warning(f"获取每日结果时发生错误: {str(e)}")

        return daily_df

    def _process_trades(self, engine) -> List[Dict[str, Any]]:
        """处理回测交易记录

        Args:
            engine: 回测引擎实例

        Returns:
            list: 处理后的交易记录列表
        """
        trades = []

        try:
            # 首先尝试调用get_all_trades方法
            for trade in engine.get_all_trades():
                trade_dict = {
                    "datetime": trade.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "symbol": trade.symbol,
                    "exchange": trade.exchange.value,
                    "direction": trade.direction.value,
                    "offset": trade.offset.value,
                    "price": float(trade.price),
                    "volume": float(trade.volume),
                    "vt_tradeid": trade.vt_tradeid,
                    # Safely access pnl, defaulting to None if not present or not an attribute
                    "pnl": self._convert_to_json_serializable(getattr(trade, 'pnl', None))
                }
                trades.append(trade_dict)
        except AttributeError:
            # 尝试从不同属性获取交易记录
            if hasattr(engine, 'trades'):
                trades = self._extract_trades_from_dict(engine.trades)
            elif hasattr(engine, 'engine') and hasattr(engine.engine, 'trades'):
                trades = self._extract_trades_from_dict(engine.engine.trades)
            else:
                logger.warning("回测引擎没有get_all_trades()方法或trades属性")
        except Exception as e:
            logger.warning(f"获取交易记录时发生错误: {str(e)}")

        return trades

    def _extract_trades_from_dict(self, trades_dict) -> List[Dict[str, Any]]:
        """从交易字典中提取交易记录

        Args:
            trades_dict: 交易记录字典

        Returns:
            list: 处理后的交易记录列表
        """
        trades = []
        for _, trade in trades_dict.items():
            trade_dict = {
                "datetime": trade.datetime.strftime("%Y-%m-%d %H:%M:%S") if hasattr(trade, 'datetime') else '',
                "symbol": trade.symbol if hasattr(trade, 'symbol') else '',
                "exchange": trade.exchange.value if hasattr(trade, 'exchange') else '',
                "direction": trade.direction.value if hasattr(trade, 'direction') else '',
                "offset": trade.offset.value if hasattr(trade, 'offset') else '',
                "price": float(trade.price) if hasattr(trade, 'price') else 0.0,
                "volume": float(trade.volume) if hasattr(trade, 'volume') else 0.0,
                "vt_tradeid": trade.vt_tradeid if hasattr(trade, 'vt_tradeid') else '',
                "pnl": self._convert_to_json_serializable(getattr(trade, 'pnl', None))
            }
            trades.append(trade_dict)
        return trades

    def _convert_to_json_serializable(self, obj: Any) -> Any:
        """转换对象为JSON可序列化格式

        Args:
            obj: 任意类型的对象

        Returns:
            转换后的JSON可序列化对象
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            if np.isnan(obj):
                return None
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (int)):
            return int(obj)
        elif isinstance(obj, (float)):
            if obj != obj:  # Check for NaN
                return None
            return float(obj)
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        elif isinstance(obj, Dict):
            return {k: self._convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        return obj

    def _get_daily_results(self, stats):
        """从统计结果中提取每日结果"""
        try:
            if isinstance(stats, dict) and 'daily_df' in stats:
                daily_df = stats['daily_df']
                if isinstance(daily_df, pd.DataFrame):
                    # 确保日期列是字符串格式
                    if 'date' in daily_df.columns:
                        daily_df['date'] = daily_df['date'].apply(lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else str(x))
                    return daily_df.to_dict(orient='records')
            return []
        except Exception as e:
            logger.warning(f"处理每日结果时出错: {e}")
            return []

    def _get_trades(self, stats):
        """从统计结果中提取交易记录

        为了避免数据库字段长度限制，只返回前100条交易记录。
        """
        try:
            if isinstance(stats, dict) and 'trades' in stats:
                trades = stats['trades']
                if isinstance(trades, list):
                    limited_trades = trades[:100] if len(trades) > 100 else trades
                    return limited_trades
            return []
        except Exception as e:
            logger.warning(f"处理交易记录时出错: {e}")
            return []

    def _save_backtest_record(self, user_id, strategy_id, symbol, exchange, interval,
                             start, end, initial_capital, stats, final_params, rate=0.0001, slippage=0, trades=None) -> Optional[int]:
        """保存回测记录到数据库

        Args:
            user_id: 用户ID
            strategy_id: 策略ID
            symbol: 交易品种符号
            exchange: 交易所
            interval: 时间间隔
            start: 开始日期
            end: 结束日期
            initial_capital: 初始资金
            stats: 回测统计结果
            final_params: 策略参数
            rate: 手续费率
            slippage: 滑点

        Returns:
            int: 回测记录ID，如果保存失败则返回None
        """
        try:
            with SessionLocal() as db:
                # 转换统计数据和参数为JSON可序列化格式
                serialized_stats = self._convert_to_json_serializable(stats)
                serialized_params = self._convert_to_json_serializable(final_params)

                # 获取策略信息
                strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
                strategy_name = strategy.name if strategy else f"Strategy {strategy_id}"
                strategy_class_name = strategy.identifier if strategy else "Unknown"

                # 将统计数据和参数转换为 JSON 字符串
                statistics_json = json.dumps(serialized_stats)
                parameters_json = json.dumps(serialized_params)

                # 将每日结果和交易记录转换为 JSON 字符串
                daily_results = self._get_daily_results(stats)
                daily_results_json = json.dumps(daily_results) if daily_results else "[]"

                # 处理交易记录
                if trades is not None:
                    # 限制交易记录数量
                    limited_trades = trades[:100] if len(trades) > 100 else trades
                    trades_json = json.dumps(limited_trades)
                else:
                    # 从 stats 中提取
                    trades_from_stats = self._get_trades(stats)
                    trades_json = json.dumps(trades_from_stats) if trades_from_stats else "[]"

                # 创建回测记录
                backtest_record = BacktestRecord(
                    user_id=user_id,
                    strategy_id=strategy_id,
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    start_date=start,
                    end_date=end,
                    initial_capital=float(initial_capital),
                    final_capital=float(stats.get("end_balance", 0.0)),
                    total_return=float(stats.get("total_return", 0.0)),
                    annual_return=float(stats.get("annual_return", 0.0)),
                    max_drawdown=float(stats.get("max_ddpercent", 0.0)),
                    sharpe_ratio=float(stats.get("sharpe_ratio", 0.0)),
                    results={
                        "statistics": serialized_stats,
                        "parameters": serialized_params
                    },
                    created_at=datetime.now(),
                    # 新增字段
                    strategy_name=strategy_name,
                    strategy_class_name=strategy_class_name,
                    statistics=statistics_json,
                    parameters=parameters_json,
                    daily_results_json=daily_results_json,
                    trades_json=trades_json,
                    capital=str(initial_capital),
                    rate=str(rate),
                    slippage=str(slippage),
                    mode="bar",
                    ran_at=datetime.now()
                )

                # 保存到数据库
                db.add(backtest_record)
                db.commit()
                db.refresh(backtest_record)  # 确保可以获取到自增 ID

                # 打印日志，帮助调试
                logger.info(f"回测记录已保存至数据库，记录ID: {backtest_record.id}")

                # 返回回测记录ID
                return backtest_record.id
        except Exception as e:
            logger.error(f"保存回测记录到数据库失败: {str(e)}")
            logger.debug(traceback.format_exc())
            return None

    def run_backtest(self, strategy_id, symbol, exchange, interval, start_date, end_date, initial_capital, rate, slippage, parameters=None, user_id=None):
        """运行回测并返回结果

        Args:
            strategy_id (int): 策略ID
            symbol (str): 交易品种符号
            exchange (str): 交易所
            interval (str): 时间间隔
            start_date (date): 开始日期
            end_date (date): 结束日期
            initial_capital (float): 初始资金
            rate (float): 手续费率
            slippage (float): 滑点大小
            parameters (dict, optional): 策略参数
            user_id (int, optional): 用户ID

        Returns:
            dict: 回测结果
        """
        logger.info(f"开始回测策略 ID {strategy_id}: {start_date} 至 {end_date}")
        if parameters:
            logger.info(f"使用参数: {parameters}")

        try:
            # 获取策略
            with SessionLocal() as db:
                db_strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
                if not db_strategy:
                    raise ValueError(f"数据库中找不到策略 ID {strategy_id}")

            # 获取策略类
            strategy_class = get_strategy_class(db_strategy.identifier)
            if not strategy_class:
                raise ValueError(f"找不到策略类 {db_strategy.type}")

            # 处理日期参数
            start, end = self._prepare_date_range(start_date, end_date)

            # 获取策略类型和默认参数
            strategy_type = db_strategy.strategy_type

            # 如果策略类型为空，尝试从策略的type字段获取
            if not strategy_type and hasattr(db_strategy, 'type') and db_strategy.type:
                strategy_type = db_strategy.type.lower()
                logger.info(f"从策略的type字段获取类型: {strategy_type}")

            # 如果仍然为空，使用默认的CTA类型
            if not strategy_type:
                logger.warning(f"策略 ID {strategy_id} 的类型为空，使用默认的CTA类型")
                strategy_type = "cta"

            default_params = db_strategy.parameters

            # 使用工厂创建合适的回测引擎
            engine = self.backtest_engine_factory.create_engine(strategy_type)

            # 处理策略参数
            final_params = self._prepare_parameters(default_params, parameters)

            # 检查并转换时间间隔和交易所
            interval_obj = _get_vnpy_interval(interval)
            if not interval_obj:
                raise ValueError(f"无效的时间间隔: {interval}")

            exchange_obj = _get_vnpy_exchange(exchange)
            if not exchange_obj:
                raise ValueError(f"无效的交易所: {exchange}")

            # 构建VT符号
            vt_symbol = f"{symbol}.{exchange_obj.value}"

            # 设置回测引擎参数
            engine.set_parameters(
                vt_symbol=vt_symbol,
                interval=interval_obj,
                start=start,
                end=end,
                rate=float(rate),
                slippage=float(slippage),
                size=float(default_params.get("size", 1.0)),
                pricetick=float(default_params.get("pricetick", 0.01)),
                capital=float(initial_capital),
                mode=BacktestingMode.BAR
            )

            # 添加策略
            engine.add_strategy(strategy_class, final_params)

            # 加载历史数据
            engine.load_data()

            # 检查是否加载了数据
            if not engine.history_data:
                logger.warning(f"未加载到数据: {vt_symbol}, {interval}, {start_date} 至 {end_date}")
                return {
                    "success": False,
                    "message": f"未加载到数据: {vt_symbol}, {interval}, {start_date} 至 {end_date}"
                }

            logger.info(f"成功加载 {len(engine.history_data)} 条历史数据")

            # 运行回测
            engine.run_backtesting()
            engine.calculate_result()       # CORRECT ORDER: calculate_result must be called before calculate_statistics

            # 获取并处理每日结果，以便计算盈亏比
            daily_df = self._process_daily_results(engine)

            # 计算回测结果对象初始化
            result = {
                "success": True,
                "statistics": {},
                "daily_results": [],
                "trades": []
            }

            # 处理引擎计算的标准统计指标
            stats = engine.calculate_statistics()
            for key, value in stats.items():
                try:
                    result["statistics"][key] = self._convert_to_json_serializable(value)
                except Exception as e:
                    logger.warning(f"处理统计指标 {key} 时出错: {str(e)}")
                    result["statistics"][key] = None

            # Calculate Profit Factor (盈亏比) from daily PnL
            gross_profit = 0.0
            gross_loss = 0.0

            if not daily_df.empty and 'net_pnl' in daily_df.columns:
                for daily_net_pnl_value in daily_df['net_pnl']:
                    if daily_net_pnl_value > 0:
                        gross_profit += daily_net_pnl_value
                    elif daily_net_pnl_value < 0:
                        gross_loss += abs(daily_net_pnl_value)

            if gross_loss > 0:
                profit_factor = gross_profit / gross_loss
            elif gross_profit > 0:  # Only profit, no loss
                profit_factor = float('inf')
            else:  # No profit and no loss, or only zero-pnl trades
                profit_factor = 0.0

            result["statistics"]["profit_factor"] = self._convert_to_json_serializable(profit_factor)

            # Keep win_rate as None for now, or until it's properly calculated
            if "win_rate" not in result["statistics"]:
                 result["statistics"]["win_rate"] = None

            logger.info(f"最终回测统计数据: {result['statistics']}")

            # 处理每日结果 (daily_df 已经获取)
            if isinstance(daily_df, pd.DataFrame) and not daily_df.empty:
                result["daily_results"] = daily_df.to_dict(orient="records")

            # 获取并处理交易记录
            result["trades"] = self._process_trades(engine)

            # 记录回测结果
            logger.info(f"回测完成，收益率: {result['statistics'].get('total_return', 0.0) * 100:.2f}%, 夏普比率: {result['statistics'].get('sharpe_ratio', 0.0):.2f}")

            # 如果提供了用户ID，保存回测记录
            if user_id is not None:
                record_id = self._save_backtest_record(
                    user_id, strategy_id, symbol, exchange, interval,
                    start, end, initial_capital, stats, final_params, rate, slippage,
                    trades=result["trades"]
                )
                if record_id:
                    # 在多个位置设置回测ID，确保前端能找到
                    result["record_id"] = record_id
                    result["id"] = record_id
                    # 在统计数据中也设置回测ID
                    if "statistics" in result and isinstance(result["statistics"], dict):
                        result["statistics"]["record_id"] = record_id
                        result["statistics"]["id"] = record_id

                    # 打印日志，帮助调试
                    logger.info(f"回测记录ID: {record_id}")

            return result

        except Exception as e:
            logger.error(f"回测过程中发生错误: {str(e)}")
            traceback.print_exc()
            return {"success": False, "error": str(e), "statistics": {}, "daily_results": [], "trades": []}

    def get_backtest_records(self, user_id: Optional[int] = None,
                           strategy_id: Optional[int] = None,
                           page: int = 1,
                           page_size: int = 10) -> Tuple[List[Dict[str, Any]], int]:
        """获取回测记录列表，支持分页

        Args:
            user_id (int, optional): 用户ID
            strategy_id (int, optional): 策略ID
            page (int): 页码，从1开始
            page_size (int): 每页数量

        Returns:
            Tuple[List[Dict[str, Any]], int]: (回测记录列表, 总数量)
        """
        with SessionLocal() as db:
            query = db.query(BacktestRecord)

            if user_id is not None:
                query = query.filter(BacktestRecord.user_id == user_id)
            if strategy_id is not None:
                query = query.filter(BacktestRecord.strategy_id == strategy_id)

            # 获取总数量
            total_count = query.count()

            # 分页查询
            records = query.order_by(BacktestRecord.created_at.desc())\
                .offset((page - 1) * page_size)\
                .limit(page_size)\
                .all()

            # 将记录转换为字典列表
            result = []
            for record in records:
                # 获取策略名称
                strategy_name = getattr(record, 'strategy_name', None)
                if not strategy_name:
                    strategy = db.query(Strategy).filter(Strategy.id == record.strategy_id).first()
                    strategy_name = strategy.name if strategy else f"Strategy {record.strategy_id}"

                # 构建记录字典
                record_dict = {
                    "id": str(record.id),
                    "user_id": str(record.user_id),
                    "strategy_id": str(record.strategy_id),
                    "strategy_name": strategy_name,
                    "symbol": record.symbol,
                    "exchange": record.exchange,
                    "interval": record.interval,
                    "start_date": record.start_date.isoformat(),
                    "end_date": record.end_date.isoformat(),
                    "initial_capital": float(record.initial_capital),
                    "final_capital": float(record.final_capital) if record.final_capital else None,
                    "total_return": float(record.total_return) if record.total_return else None,
                    "annual_return": float(record.annual_return) if record.annual_return else None,
                    "max_drawdown": float(record.max_drawdown) if record.max_drawdown else None,
                    "sharpe_ratio": float(record.sharpe_ratio) if record.sharpe_ratio else None,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                    "ran_at": record.ran_at.isoformat() if hasattr(record, 'ran_at') and record.ran_at else None
                }
                result.append(record_dict)

            return result, total_count

    def get_backtest_record_detail(self, record_id: str) -> Optional[Dict[str, Any]]:
        """获取单个回测记录的详情，包括JSON格式的trades和daily_results。"""
        db = SessionLocal()
        try:
            record = db.query(BacktestRecord).filter(BacktestRecord.id == record_id).first()
            if not record:
                return None

            # 获取策略信息
            strategy = db.query(Strategy).filter(Strategy.id == record.strategy_id).first()
            strategy_name = getattr(strategy, 'name', None) if strategy else None

            # 如果记录中没有 strategy_name 字段，使用策略表中的名称
            record_strategy_name = getattr(record, 'strategy_name', None)
            if not record_strategy_name and strategy_name:
                record_strategy_name = strategy_name
            elif not record_strategy_name:
                record_strategy_name = f"Strategy {record.strategy_id}"

            # 如果记录中没有 strategy_class_name 字段，使用默认值
            record_class_name = getattr(record, 'strategy_class_name', None)
            if not record_class_name and strategy:
                record_class_name = strategy.identifier
            elif not record_class_name:
                record_class_name = "Unknown"

            # 如果记录中没有 statistics 字段，从 results 中获取
            record_statistics = getattr(record, 'statistics', None)
            if not record_statistics and hasattr(record, 'results') and record.results:
                if isinstance(record.results, dict) and 'statistics' in record.results:
                    record_statistics = json.dumps(record.results['statistics'])
                else:
                    record_statistics = "{}"
            elif not record_statistics:
                record_statistics = "{}"

            statistics_data = json.loads(record_statistics) if isinstance(record_statistics, str) else record_statistics

            # 处理NaN和Infinity
            for key, value in statistics_data.items():
                 if isinstance(value, float) and (pd.isna(value) or value == float('inf') or value == float('-inf')):
                    statistics_data[key] = str(value)
                 elif isinstance(value, pd.Timestamp):
                     statistics_data[key] = value.isoformat()

            # 如果记录中没有 parameters 字段，从 results 中获取
            record_parameters = getattr(record, 'parameters', None)
            if not record_parameters and hasattr(record, 'results') and record.results:
                if isinstance(record.results, dict) and 'parameters' in record.results:
                    record_parameters = json.dumps(record.results['parameters'])
                else:
                    record_parameters = "{}"
            elif not record_parameters:
                record_parameters = "{}"

            # 如果记录中没有 capital, rate, slippage, mode 字段，使用默认值
            record_capital = getattr(record, 'capital', None)
            if not record_capital:
                record_capital = record.initial_capital

            record_rate = getattr(record, 'rate', None)
            if not record_rate:
                record_rate = 0.0001

            record_slippage = getattr(record, 'slippage', None)
            if not record_slippage:
                record_slippage = 0

            record_mode = getattr(record, 'mode', None)
            if not record_mode:
                record_mode = "bar"

            # 如果记录中没有 daily_results_json 和 trades_json 字段，使用空列表
            record_daily_results = getattr(record, 'daily_results_json', None)
            if not record_daily_results:
                record_daily_results = "[]"

            record_trades = getattr(record, 'trades_json', None)
            if not record_trades:
                record_trades = "[]"

            # 如果记录中没有 ran_at 字段，使用 created_at 或当前时间
            record_ran_at = getattr(record, 'ran_at', None)
            if not record_ran_at:
                record_ran_at = record.created_at if hasattr(record, 'created_at') else datetime.now()

            return {
                "id": str(record.id),
                "user_id": str(record.user_id) if record.user_id else None,
                "strategy_id": str(record.strategy_id) if record.strategy_id else None,
                "strategy_name": record_strategy_name,
                "strategy_class_name": record_class_name,
                "symbol": record.symbol,
                "exchange": record.exchange,
                "interval": record.interval,
                "start_date": record.start_date.isoformat(),
                "end_date": record.end_date.isoformat(),
                "capital": record_capital,
                "rate": record_rate,
                "slippage": record_slippage,
                "mode": record_mode,
                "parameters": json.loads(record_parameters) if isinstance(record_parameters, str) else record_parameters,
                "statistics": statistics_data,
                "daily_results_json": record_daily_results,
                "trades_json": record_trades,
                "ran_at": record_ran_at.isoformat() if hasattr(record_ran_at, 'isoformat') else str(record_ran_at)
            }
        except Exception as e:
            logger.error(f"获取回测记录详情失败: {e}")
            traceback.print_exc()
            return None
        finally:
            db.close()

    def get_backtest_report_data(self, backtest_id: str) -> Optional[BacktestReportDataModel]:
        """根据backtest_id获取详细的回测报告数据"""
        logger.info(f"开始获取回测报告数据，ID: {backtest_id}")
        db = SessionLocal()
        try:
            # 查询回测记录
            logger.info(f"查询回测记录，ID: {backtest_id}")
            record = db.query(BacktestRecord).filter(BacktestRecord.id == backtest_id).first()

            # 如果记录不存在，返回None
            if not record:
                logger.warning(f"未找到ID为 {backtest_id} 的回测记录")
                return None

            # 记录找到的回测记录信息
            logger.info(f"找到回测记录，ID: {backtest_id}, 策略ID: {record.strategy_id}, 符号: {record.symbol}")

            # 1. 构建配置信息
            # 获取策略信息
            strategy = db.query(Strategy).filter(Strategy.id == record.strategy_id).first()
            strategy_name = getattr(strategy, 'name', None) if strategy else None

            # 如果记录中没有 strategy_name 字段，使用策略表中的名称
            record_strategy_name = getattr(record, 'strategy_name', None)
            if not record_strategy_name and strategy_name:
                record_strategy_name = strategy_name
            elif not record_strategy_name:
                record_strategy_name = f"Strategy {record.strategy_id}"

            # 如果记录中没有 strategy_class_name 字段，使用默认值
            record_class_name = getattr(record, 'strategy_class_name', None)
            if not record_class_name and strategy:
                record_class_name = strategy.identifier
            elif not record_class_name:
                record_class_name = "Unknown"

            # 如果记录中没有 parameters 字段，从 results 中获取
            record_parameters = getattr(record, 'parameters', None)
            if not record_parameters and hasattr(record, 'results') and record.results:
                if isinstance(record.results, dict) and 'parameters' in record.results:
                    record_parameters = json.dumps(record.results['parameters'])
                else:
                    record_parameters = "{}"
            elif not record_parameters:
                record_parameters = "{}"

            # 如果记录中没有 capital, rate, slippage, mode 字段，使用默认值
            record_capital = getattr(record, 'capital', None)
            if not record_capital:
                record_capital = record.initial_capital

            record_rate = getattr(record, 'rate', None)
            if not record_rate:
                record_rate = 0.0001

            record_slippage = getattr(record, 'slippage', None)
            if not record_slippage:
                record_slippage = 0

            record_mode = getattr(record, 'mode', None)
            if not record_mode:
                record_mode = "bar"

            # 构建配置数据
            config_data = {
                "strategy_id": str(record.strategy_id),
                "strategy_name": record_strategy_name,
                "class_name": record_class_name,
                "symbol": record.symbol,
                "exchange": record.exchange,
                "interval": record.interval,
                "start_date": record.start_date,
                "end_date": record.end_date,
                "capital": float(record_capital),
                "rate": float(record_rate),
                "slippage": float(record_slippage),
                "mode": record_mode,
                "parameters": json.loads(record_parameters) if isinstance(record_parameters, str) else record_parameters
            }

            report_config = BacktestReportConfigModel(**config_data)

            # 2. 提取统计摘要
            record_statistics = getattr(record, 'statistics', None)
            if not record_statistics and hasattr(record, 'results') and record.results:
                if isinstance(record.results, dict) and 'statistics' in record.results:
                    record_statistics = json.dumps(record.results['statistics'])
                else:
                    record_statistics = "{}"
            elif not record_statistics:
                record_statistics = "{}"

            summary_stats = json.loads(record_statistics) if isinstance(record_statistics, str) else record_statistics

            # 对summary_stats中的NaN和Infinity进行处理
            for key, value in summary_stats.items():
                if isinstance(value, float) and (pd.isna(value) or value == float('inf') or value == float('-inf')):
                    summary_stats[key] = str(value)
                elif isinstance(value, pd.Timestamp):
                     summary_stats[key] = value.isoformat()

            # 3. 处理资金曲线
            equity_curve_data = []
            record_daily_results = getattr(record, 'daily_results_json', None)
            if record_daily_results:
                try:
                    daily_df = pd.read_json(record_daily_results)
                    if not daily_df.empty and 'date' in daily_df.columns and 'balance' in daily_df.columns:
                         # 确保 'date' 列是 datetime 类型，然后转换为 date
                        daily_df['date'] = pd.to_datetime(daily_df['date']).dt.date
                        for _, row in daily_df.iterrows():
                            equity_curve_data.append(
                                EquityCurvePointModel(date=row['date'], equity=row['balance'])
                            )
                except Exception as e:
                    logger.warning(f"处理资金曲线数据时出错: {e}")

            # 如果没有资金曲线数据，创建一个简单的模拟数据
            if not equity_curve_data:
                start_date = record.start_date
                end_date = record.end_date
                initial_capital = float(record_capital)
                final_capital = float(record.final_capital) if record.final_capital else initial_capital

                # 创建两个点的资金曲线
                equity_curve_data = [
                    EquityCurvePointModel(date=start_date, equity=initial_capital),
                    EquityCurvePointModel(date=end_date, equity=final_capital)
                ]

            # 4. 处理交易详情
            trades_data = []
            record_trades = getattr(record, 'trades_json', None)
            if record_trades:
                try:
                    trades_list_of_dicts = json.loads(record_trades)
                    for trade_dict in trades_list_of_dicts:
                        # 将字符串日期时间转换为datetime对象
                        if 'datetime' in trade_dict and isinstance(trade_dict['datetime'], str):
                            try:
                                trade_dict['datetime'] = datetime.fromisoformat(trade_dict['datetime'])
                            except ValueError:
                                 # 尝试其他常见格式，如果需要
                                try:
                                    trade_dict['datetime'] = datetime.strptime(trade_dict['datetime'], "%Y-%m-%d %H:%M:%S.%f")
                                except ValueError:
                                    logger.warning(f"无法解析交易记录中的日期时间: {trade_dict['datetime']}")
                                    continue # 跳过此交易记录

                        # 确保pnl是float或None
                        if 'pnl' in trade_dict and trade_dict['pnl'] is not None:
                            try:
                                trade_dict['pnl'] = float(trade_dict['pnl'])
                            except (ValueError, TypeError):
                                trade_dict['pnl'] = None
                        else:
                            trade_dict['pnl'] = None

                        trades_data.append(TradeDetailOutputModel(**trade_dict))
                except Exception as e:
                    logger.warning(f"处理交易详情数据时出错: {e}")

            # 如果没有交易数据，创建一个空列表
            if not trades_data:
                trades_data = []

            # 5. 获取执行时间
            record_ran_at = getattr(record, 'ran_at', None)
            if not record_ran_at:
                record_ran_at = record.created_at if hasattr(record, 'created_at') else datetime.now()

            # 构建报告数据模型
            logger.info(f"构建回测报告数据模型，ID: {backtest_id}")
            try:
                report_data = BacktestReportDataModel(
                    backtest_id=str(record.id),
                    ran_at=record_ran_at,
                    config=report_config,
                    summary_stats=summary_stats,
                    equity_curve=equity_curve_data,
                    trades=trades_data
                )
                logger.info(f"成功构建回测报告数据模型，ID: {backtest_id}")
                return report_data
            except Exception as model_error:
                logger.error(f"构建回测报告数据模型时出错，ID: {backtest_id}, 错误: {model_error}")
                # 输出模型构建所需的数据结构
                logger.error(f"backtest_id: {type(record.id)}, ran_at: {type(record_ran_at)}, config: {type(report_config)}, summary_stats: {type(summary_stats)}")
                traceback.print_exc()
                raise
        except Exception as e:
            logger.error(f"获取回测报告 {backtest_id} 时出错: {e}")
            traceback.print_exc()
            return None
        finally:
            db.close()
            logger.info(f"完成获取回测报告数据，ID: {backtest_id}")

    # 其他方法保持不变...
