"""
回测服务

提供策略回测功能。
"""

import logging
import traceback
import json
from datetime import datetime, date
from typing import List, Optional, Any, Dict, Union
import numpy as np
import pandas as pd

from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.database import get_database
from vnpy.trader.setting import SETTINGS
from vnpy_ctastrategy.backtesting import BacktestingMode


from simpletrade.config.database import SessionLocal
from simpletrade.models.database import Strategy, BacktestRecord
from simpletrade.strategies import get_strategy_class
from simpletrade.config import settings
from simpletrade.services.backtest_engines import BacktestEngineFactory

logger = logging.getLogger("simpletrade.services.backtest_service")

# Helper function to convert string interval to VnPy Interval enum
def _get_vnpy_interval(interval_str: str) -> Optional[Interval]:
    interval_map = {
        "1m": Interval.MINUTE,
        # Add other supported intervals by Qlib Importer AND VnPy backtester here
        # "5m": Interval.MIN5,  # Assuming these are the correct names now
        # "15m": Interval.MIN15,
        # "30m": Interval.MIN30,
        "1h": Interval.HOUR,
        # "4h": Interval.HOUR4,
        "d": Interval.DAILY,
        "w": Interval.WEEKLY,
    }
    return interval_map.get(interval_str)

# Helper function to convert string exchange to VnPy Exchange enum
def _get_vnpy_exchange(exchange_str: str) -> Optional[Exchange]:
    try:
        return Exchange(exchange_str.upper()) # Try direct conversion (e.g., "SHFE")
    except ValueError:
        # Add mappings if needed, e.g., "XSHG" -> Exchange.SSE
        logger.warning(f"Could not directly convert '{exchange_str}' to Exchange enum. Returning None.")
        return None

def ensure_mysql_database():
    """确保VnPy使用MySQL数据库"""
    # 检查全局设置中的数据库类型
    if SETTINGS.get("database.driver", None) != "mysql":
        logger.info("Setting VnPy database to MySQL")
        # 配置MySQL连接
        mysql_settings = {
            "database.driver": "mysql",
            "database.host": settings.MYSQL_SERVER,
            "database.port": settings.MYSQL_PORT,
            "database.database": settings.MYSQL_DATABASE,
            "database.user": settings.MYSQL_USERNAME,
            "database.password": settings.MYSQL_PASSWORD,
        }
        # 更新VnPy全局设置
        SETTINGS.update(mysql_settings)
        
    # 获取并返回数据库实例
    return get_database()

class BacktestService:
    """回测服务"""
    
    def __init__(self):
        """初始化"""
        self.db_session = SessionLocal()
    
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
            
            # 如果start_date和end_date是日期对象，转换为字符串
            if hasattr(start_date, 'isoformat'):
                start_date_str = start_date.isoformat()
            else:
                start_date_str = str(start_date)
                
            if hasattr(end_date, 'isoformat'):
                end_date_str = end_date.isoformat()
            else:
                end_date_str = str(end_date)
            
            # 转换日期字符串为datetime对象
            start = datetime.strptime(start_date_str, "%Y-%m-%d")
            end = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            # 获取策略默认参数
            default_params = db_strategy.parameters
            
            # 获取策略类型
            strategy_type = db_strategy.strategy_type
            
            # 使用工厂创建合适的回测引擎
            engine = BacktestEngineFactory.create_engine(strategy_type)
            
            # 合并默认参数和用户传入的参数
            final_params = {**default_params}
            if parameters:
                final_params.update(parameters)
                
            # 设置回测引擎参数
            interval_obj = _get_vnpy_interval(interval)
            if not interval_obj:
                raise ValueError(f"无效的时间间隔: {interval}")
            
            # 解析交易对
            exchange_obj = _get_vnpy_exchange(exchange)
            if not exchange_obj:
                raise ValueError(f"无效的交易所: {exchange}")
            
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
                pricetick=float(default_params.get("pricetick", 0.0)),
                capital=float(initial_capital),
                mode=BacktestingMode.BAR
            )
            
            # 添加策略
            engine.add_strategy(strategy_class, final_params)
            
            # 加载历史数据
            engine.load_data()
            
            # 检查是否成功加载了数据
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
            
            # 获取每日结果
            try:
                # 首先尝试调用get_daily_results()方法
                daily_df = engine.get_daily_results()
                
                # 如果daily_df不是DataFrame类型，尝试转换
                if not isinstance(daily_df, pd.DataFrame):
                    daily_df = pd.DataFrame(daily_df) if daily_df else pd.DataFrame()
                
                # 如果daily_df不为空，转换数据类型
                if not daily_df.empty:
                    for col in daily_df.columns:
                        if col != "date":
                            try:
                                daily_df[col] = pd.to_numeric(daily_df[col], errors='coerce')
                            except Exception as e:
                                logger.warning(f"转换列 {col} 为数字类型时出错: {str(e)}")
                                # 如果转换失败，使用空值填充
                                daily_df[col] = None
            except AttributeError:
                # 如果方法不存在，尝试直接访问daily_df属性
                if hasattr(engine, 'daily_df'):
                    daily_df = engine.daily_df
                    # 确保是DataFrame
                    if not isinstance(daily_df, pd.DataFrame):
                        daily_df = pd.DataFrame(daily_df) if daily_df else pd.DataFrame()
                elif hasattr(engine.engine, 'daily_df'):
                    # 如果是wrapper类，尝试访问内部engine的属性
                    daily_df = engine.engine.daily_df
                    # 确保是DataFrame
                    if not isinstance(daily_df, pd.DataFrame):
                        daily_df = pd.DataFrame(daily_df) if daily_df else pd.DataFrame()
                else:
                    # 如果都不存在，创建一个空的DataFrame
                    logger.warning("回测引擎没有get_daily_results()方法或daily_df属性，使用空DataFrame")
                    daily_df = pd.DataFrame()
            except Exception as e:
                logger.warning(f"获取每日结果时发生错误: {str(e)}")
                # 创建一个空的DataFrame
                daily_df = pd.DataFrame()
            
            # 获取交易记录
            trades = []
            try:
                # 尝试调用get_all_trades方法
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
                # 如果方法不存在，尝试直接访问trades属性
                if hasattr(engine, 'trades'):
                    for trade_id, trade in engine.trades.items():
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
                elif hasattr(engine.engine, 'trades'):
                    # 如果是wrapper类，尝试访问内部engine的属性
                    for trade_id, trade in engine.engine.trades.items():
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
                else:
                    logger.warning("回测引擎没有get_all_trades()方法或trades属性")
            
            # 构建最终结果
            result = {
                "success": True,
                "statistics": {}
            }
            
            # 安全处理统计指标
            for key, value in stats.items():
                try:
                    # 处理特殊类型
                    if isinstance(value, (np.float32, np.float64, np.int32, np.int64)):
                        value = float(value)
                    elif isinstance(value, (list, tuple, np.ndarray)):
                        # 对于数组类型，转换为列表
                        value = value.tolist() if hasattr(value, 'tolist') else list(value)
                    result["statistics"][key] = value
                except Exception as e:
                    logger.warning(f"处理统计指标 {key} 时出错: {str(e)}")
                    result["statistics"][key] = None
            
            # 安全处理日线结果
            try:
                if isinstance(daily_df, pd.DataFrame) and not daily_df.empty:
                    result["daily_results"] = daily_df.to_dict(orient="records")
                else:
                    result["daily_results"] = []
            except Exception as e:
                logger.warning(f"处理日线结果时出错: {str(e)}")
                result["daily_results"] = []
            
            # 安全处理交易记录
            result["trades"] = trades
            
            logger.info(f"回测完成，收益率: {stats.get('total_return', 0.0) * 100:.2f}%, 夏普比率: {stats.get('sharpe_ratio', 0.0):.2f}")
            
            # 如果提供了user_id则保存回测记录到数据库
            if user_id is not None:
                try:
                    with SessionLocal() as db:
                        # 转换日期和NumPy类型为JSON可序列化的格式
                        def json_serialize(obj: Any) -> Any:
                            """转换特殊类型为JSON可序列化的格式"""
                            if isinstance(obj, (datetime, date)):
                                return obj.isoformat()
                            elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, 
                                                np.uint8, np.uint16, np.uint32, np.uint64)):
                                return int(obj)
                            elif isinstance(obj, (np.float16, np.float32, np.float64)):
                                return float(obj)
                            elif isinstance(obj, (np.ndarray,)):
                                return obj.tolist()
                            elif isinstance(obj, Dict):
                                return {k: json_serialize(v) for k, v in obj.items()}
                            elif isinstance(obj, list):
                                return [json_serialize(item) for item in obj]
                            return obj
                            
                        # 转换统计数据和参数
                        serialized_stats = json_serialize(result["statistics"])
                        serialized_params = json_serialize(final_params)
                        
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
                        db.add(backtest_record)
                        db.commit()
                        logger.info(f"回测记录已保存至数据库，记录ID: {backtest_record.id}")
                        # 添加记录ID到结果中
                        result["record_id"] = backtest_record.id
                except Exception as db_error:
                    logger.error(f"保存回测记录到数据库失败: {str(db_error)}")
                    logger.debug(traceback.format_exc())
                    # 不要因为保存记录失败而影响回测结果的返回
            
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
        """
        获取回测记录
        
        参数:
            user_id (int, optional): 用户ID
            strategy_id (int, optional): 策略ID
            
        返回:
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
        """
        获取回测记录
        
        参数:
            record_id (int): 回测记录ID
            
        返回:
            BacktestRecord: 回测记录，如果不存在则返回None
        """
        with SessionLocal() as db:
            return db.query(BacktestRecord).filter(BacktestRecord.id == record_id).first()
