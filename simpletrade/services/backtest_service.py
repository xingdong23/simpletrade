"""
回测服务

提供策略回测功能。
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.trader.constant import Interval

from simpletrade.config.database import get_db
from simpletrade.models.database import Strategy, BacktestRecord
from simpletrade.strategies import get_strategy_class
from simpletrade.services.strategy_service import StrategyService

logger = logging.getLogger("simpletrade.services.backtest_service")

class BacktestService:
    """回测服务"""
    
    def __init__(self):
        """初始化"""
        self.engine = BacktestingEngine()
    
    def run_backtest(self, strategy_id: int, symbol: str, exchange: str, 
                    interval: str, start_date: str, end_date: str, 
                    initial_capital: float = 100000.0, 
                    rate: float = 0.0003, slippage: float = 0.2,
                    size: float = 1, pricetick: float = 0.2,
                    user_id: int = 1) -> Dict[str, Any]:
        """
        运行回测
        
        参数:
            strategy_id (int): 策略ID
            symbol (str): 交易品种
            exchange (str): 交易所
            interval (str): K线周期
            start_date (str): 开始日期，格式：YYYY-MM-DD
            end_date (str): 结束日期，格式：YYYY-MM-DD
            initial_capital (float, optional): 初始资金
            rate (float, optional): 手续费率
            slippage (float, optional): 滑点
            size (float, optional): 合约乘数
            pricetick (float, optional): 价格跳动
            user_id (int, optional): 用户ID
            
        返回:
            Dict[str, Any]: 回测结果
        """
        # 从数据库加载策略配置
        with get_db() as db:
            strategy = db.query(Strategy).filter(
                Strategy.id == strategy_id,
                Strategy.is_active == True
            ).first()
            
            if not strategy:
                logger.error(f"Strategy {strategy_id} not found")
                return {"success": False, "message": "Strategy not found"}
            
            # 获取策略类
            strategy_class = get_strategy_class(strategy.type)
            if not strategy_class:
                logger.error(f"Strategy class {strategy.type} not found")
                return {"success": False, "message": f"Strategy class {strategy.type} not found"}
            
            # 转换日期格式
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # 转换K线周期
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
            vnpy_interval = interval_map.get(interval, Interval.DAILY)
            
            # 设置回测参数
            self.engine.set_parameters(
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
            
            # 添加策略
            self.engine.add_strategy(
                strategy_class,
                strategy.parameters
            )
            
            try:
                # 运行回测
                self.engine.run_backtesting()
                
                # 获取回测结果
                df = self.engine.calculate_result()
                statistics = self.engine.calculate_statistics()
                
                # 保存回测记录
                record = BacktestRecord(
                    user_id=user_id,
                    strategy_id=strategy_id,
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=initial_capital,
                    final_capital=statistics["end_balance"],
                    total_return=statistics["total_return"],
                    annual_return=statistics["annual_return"],
                    max_drawdown=statistics["max_drawdown"],
                    sharpe_ratio=statistics["sharpe_ratio"],
                    results=statistics
                )
                db.add(record)
                db.commit()
                db.refresh(record)
                
                logger.info(f"Backtest for strategy {strategy.name} completed successfully")
                
                return {
                    "success": True,
                    "message": "Backtest completed successfully",
                    "data": {
                        "statistics": statistics,
                        "trades": self.engine.get_all_trades()
                    }
                }
            except Exception as e:
                logger.error(f"Failed to run backtest: {e}")
                return {"success": False, "message": f"Failed to run backtest: {e}"}
    
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
        with get_db() as db:
            query = db.query(BacktestRecord)
            
            # 应用过滤条件
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
        with get_db() as db:
            return db.query(BacktestRecord).filter(BacktestRecord.id == record_id).first()
