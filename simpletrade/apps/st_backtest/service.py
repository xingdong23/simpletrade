"""
SimpleTrade回测服务

提供策略回测服务功能。
"""

import logging
import traceback
from datetime import datetime, date
from typing import List, Optional, Any, Dict, Union, Tuple

import numpy as np
import pandas as pd

from vnpy.trader.constant import Interval
from vnpy_ctastrategy.backtesting import BacktestingMode

from simpletrade.config.database import SessionLocal
from simpletrade.models.database import Strategy, BacktestRecord
from simpletrade.strategies import get_strategy_class
from .engine import BacktestEngineFactory, _get_vnpy_interval, _get_vnpy_exchange

logger = logging.getLogger("simpletrade.apps.st_backtest.service")


class BacktestService:
    """回测服务"""
    
    def __init__(self, backtest_engine=None):
        """初始化回测服务
        
        Args:
            backtest_engine: 回测引擎实例，如果不提供则使用工厂创建
        """
        self.backtest_engine = backtest_engine
    
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
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, Dict):
            return {k: self._convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        return obj
    
    def _save_backtest_record(self, user_id, strategy_id, symbol, exchange, interval, 
                             start, end, initial_capital, stats, final_params) -> Optional[int]:
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
            
        Returns:
            int: 回测记录ID，如果保存失败则返回None
        """
        try:
            with SessionLocal() as db:
                # 转换统计数据和参数为JSON可序列化格式
                serialized_stats = self._convert_to_json_serializable(stats)
                serialized_params = self._convert_to_json_serializable(final_params)
                
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
                    created_at=datetime.now()
                )
                
                # 保存到数据库
                db.add(backtest_record)
                db.commit()
                logger.info(f"回测记录已保存至数据库，记录ID: {backtest_record.id}")
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
            default_params = db_strategy.parameters
            
            # 使用工厂创建合适的回测引擎
            engine = BacktestEngineFactory.create_engine(strategy_type)
            
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
            
            # 计算回测结果
            engine.calculate_result()
            
            # 计算统计指标
            stats = engine.calculate_statistics()
            
            # 获取并处理每日结果
            daily_df = self._process_daily_results(engine)
            
            # 获取并处理交易记录
            trades = self._process_trades(engine)
            
            # 构建结果字典
            result = {
                "success": True,
                "statistics": {},
                "daily_results": [],
                "trades": trades
            }
            
            # 处理统计指标
            for key, value in stats.items():
                try:
                    result["statistics"][key] = self._convert_to_json_serializable(value)
                except Exception as e:
                    logger.warning(f"处理统计指标 {key} 时出错: {str(e)}")
                    result["statistics"][key] = None
            
            # 处理每日结果
            if isinstance(daily_df, pd.DataFrame) and not daily_df.empty:
                result["daily_results"] = daily_df.to_dict(orient="records")
            
            # 记录回测结果
            logger.info(f"回测完成，收益率: {stats.get('total_return', 0.0) * 100:.2f}%, 夏普比率: {stats.get('sharpe_ratio', 0.0):.2f}")
            
            # 如果提供了用户ID，保存回测记录
            if user_id is not None:
                record_id = self._save_backtest_record(
                    user_id, strategy_id, symbol, exchange, interval, 
                    start, end, initial_capital, stats, final_params
                )
                if record_id:
                    result["record_id"] = record_id
            
            return result
            
        except Exception as e:
            logger.error(f"回测过程中发生错误: {str(e)}")
            logger.debug(traceback.format_exc())
            return {
                "success": False,
                "message": f"回测失败: {str(e)}"
            }
    
    def get_backtest_records(self, user_id: Optional[int] = None, 
                           strategy_id: Optional[int] = None) -> List[BacktestRecord]:
        """获取回测记录列表
        
        Args:
            user_id (int, optional): 用户ID
            strategy_id (int, optional): 策略ID
            
        Returns:
            List[BacktestRecord]: 回测记录列表
        """
        with SessionLocal() as db:
            query = db.query(BacktestRecord)
            
            if user_id is not None:
                query = query.filter(BacktestRecord.user_id == user_id)
            if strategy_id is not None:
                query = query.filter(BacktestRecord.strategy_id == strategy_id)
                
            return query.order_by(BacktestRecord.created_at.desc()).all()
    
    def get_backtest_record(self, record_id: int) -> Optional[BacktestRecord]:
        """获取回测记录详情
        
        Args:
            record_id (int): 回测记录ID
            
        Returns:
            BacktestRecord: 回测记录，如果不存在则返回None
        """
        with SessionLocal() as db:
            return db.query(BacktestRecord).filter(BacktestRecord.id == record_id).first()