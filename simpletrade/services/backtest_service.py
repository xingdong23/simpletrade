"""
回测服务

提供策略回测功能。
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
import traceback
import numpy as np

from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy.trader.constant import Interval

from simpletrade.config.database import SessionLocal
from simpletrade.models.database import Strategy, BacktestRecord
from simpletrade.strategies import get_strategy_class

logger = logging.getLogger("simpletrade.services.backtest_service")

class BacktestService:
    """回测服务"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def run_backtest(self, 
                    strategy_id: int, 
                    symbol: str, 
                    exchange: str, 
                    interval: str, 
                    start_date: date,
                    end_date: date,
                    initial_capital: float,
                    rate: float, 
                    slippage: float,
                    parameters: Optional[Dict[str, Any]] = None,
                    user_id: int = 1,
                    size: float = 1.0, 
                    pricetick: float = 0.01) -> Dict[str, Any]:
        """
        运行回测
        
        参数:
            strategy_id (int): 策略ID
            symbol (str): 交易品种
            exchange (str): 交易所
            interval (str): K线周期 (例如 '1m', '1h', 'd')
            start_date (date): 开始日期
            end_date (date): 结束日期
            initial_capital (float): 初始资金
            rate (float): 手续费率
            slippage (float): 滑点
            parameters (Dict[str, Any], optional): 用户自定义策略参数
            user_id (int, optional): 用户ID
            size (float, optional): 合约乘数
            pricetick (float, optional): 价格跳动
            
        返回:
            Dict[str, Any]: 回测结果 {success: bool, message: str, data: Optional[Dict]} 
                             data 包含 statistics 和可能的 trades
        """
        engine = BacktestingEngine()
        
        db = SessionLocal()
        try:
            strategy = db.query(Strategy).filter(
                Strategy.id == strategy_id,
                Strategy.is_active == True
            ).first()
            
            if not strategy:
                logger.error(f"Backtest failed: Strategy {strategy_id} not found")
                return {"success": False, "message": f"Strategy {strategy_id} not found", "data": None}

            if not hasattr(strategy, 'identifier') or not strategy.identifier:
                 logger.error(f"Backtest failed: Strategy {strategy.id} ({strategy.name}) is missing a valid identifier.")
                 return {"success": False, "message": f"Strategy {strategy.id} is missing identifier", "data": None}
                 
            strategy_class = get_strategy_class(strategy.identifier)
            if not strategy_class:
                logger.error(f"Backtest failed: Strategy class for identifier '{strategy.identifier}' not found")
                return {"success": False, "message": f"Strategy class '{strategy.identifier}' not found", "data": None}
            
            default_params = strategy.parameters if strategy.parameters else {}
            user_params = parameters if parameters else {}
            final_params = default_params.copy()
            try:
                final_params.update(user_params)
            except TypeError as e:
                 logger.error(f"Backtest failed: Error merging parameters. Default: {default_params}, User: {user_params}. Error: {e}")
                 return {"success": False, "message": f"Invalid user parameters format: {e}", "data": None}
            logger.info(f"Running backtest for {strategy.identifier} with final parameters: {final_params}")
            
            start = datetime.combine(start_date, datetime.min.time())
            end = datetime.combine(end_date, datetime.max.time())
            
            interval_map = {
                "1m": Interval.MINUTE,
                "5m": Interval.MINUTE5,
                "15m": Interval.MINUTE15,
                "30m": Interval.MINUTE30,
                "1h": Interval.HOUR,
                "4h": Interval.HOUR4,
                "d": Interval.DAILY,
                "w": Interval.WEEKLY,
            }
            vnpy_interval = interval_map.get(interval)
            if not vnpy_interval:
                logger.error(f"Backtest failed: Invalid interval string '{interval}'")
                return {"success": False, "message": f"Invalid interval: {interval}", "data": None}
            
            if size <= 0 or pricetick <= 0:
                 logger.warning(f"Backtest for {symbol}.{exchange}: size or pricetick is zero or negative (size={size}, pricetick={pricetick}). Using defaults 1.0 and 0.01.")
                 size = 1.0
                 pricetick = 0.01

            try:
                engine.set_parameters(
                    vt_symbol=f"{symbol}.{exchange}",
                    interval=vnpy_interval,
                    start=start,
                    end=end,
                    rate=rate,
                    slippage=slippage,
                    size=size,
                    pricetick=pricetick,
                    capital=initial_capital
                )
            except ValueError as e:
                 logger.error(f"Backtest failed: Invalid parameter for BacktestingEngine.set_parameters: {e}")
                 return {"success": False, "message": f"Invalid backtest parameter: {e}", "data": None}
            
            engine.add_strategy(
                strategy_class,
                final_params
            )
            
            try:
                logger.info(f"Starting backtest run for {strategy.identifier} ({symbol}.{exchange}) from {start_date} to {end_date}")
                engine.run_backtesting()
                logger.info(f"Backtest run finished for {strategy.identifier}")
                
                logger.info(f"Calculating backtest results...")
                df = engine.calculate_result()
                statistics = engine.calculate_statistics(output=False)
                trades = engine.get_all_trades()
                logger.info(f"Backtest statistics calculated.")
                
                cleaned_statistics = {}
                for key, value in statistics.items():
                    if isinstance(value, (float, int)) and not np.isfinite(value):
                        cleaned_statistics[key] = None
                    else:
                        cleaned_statistics[key] = value

                record = BacktestRecord(
                    user_id=user_id,
                    strategy_id=strategy_id,
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=initial_capital,
                    final_capital=cleaned_statistics.get("end_balance"),
                    total_return=cleaned_statistics.get("total_return"),
                    annual_return=cleaned_statistics.get("annual_return"),
                    max_drawdown=cleaned_statistics.get("max_drawdown"),
                    sharpe_ratio=cleaned_statistics.get("sharpe_ratio"),
                    results={
                        k: cleaned_statistics.get(k) for k in [
                            "total_days", "profit_days", "loss_days",
                            "total_net_pnl", "total_commission", "total_slippage",
                            "total_turnover", "total_trade_count",
                            "win_rate", "average_win_pnl", "average_loss_pnl",
                            "profit_factor", "return_drawdown_ratio"
                        ]
                    }
                )
                db.add(record)
                db.commit()
                db.refresh(record)
                logger.info(f"Backtest record {record.id} saved successfully for strategy {strategy.identifier}")
                
                api_return_data = {
                     "record_id": record.id,
                     "statistics": cleaned_statistics,
                }

                return {
                    "success": True,
                    "message": "Backtest completed successfully",
                    "data": api_return_data
                }

            except Exception as e:
                 logger.error(f"Failed during backtest run or result processing: {e}\n{traceback.format_exc()}")
                 db.rollback()
                 return {"success": False, "message": f"Error during backtest: {e}", "data": None}
        finally:
            if db:
                db.close()
                logger.debug("Database session closed in BacktestService.run_backtest")
    
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
