"""
策略监控服务

提供对运行中策略的实时监控功能。
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from threading import Thread
from sqlalchemy.orm import Session
# from simpletrade.config.database import get_db # Old incorrect path
from simpletrade.api.deps import get_db # Correct path for dependency injection
from simpletrade.core.engine import STMainEngine
# from simpletrade.models.database import Strategy, UserStrategy, StrategyRun, TradeRecord # Old import with missing models
from simpletrade.models.database import Strategy, UserStrategy # Corrected import

logger = logging.getLogger("simpletrade.services.monitor_service")

class StrategyMonitor:
    """策略监控类，用于监控单个策略的运行状态"""
    
    def __init__(self, strategy_name: str, user_strategy_id: int):
        """
        初始化
        
        参数:
            strategy_name (str): 策略名称
            user_strategy_id (int): 用户策略ID
        """
        self.strategy_name = strategy_name
        self.user_strategy_id = user_strategy_id
        self.start_time = datetime.now()
        self.last_update_time = datetime.now()
        self.status = "running"  # running, stopped, error
        self.error_message = ""
        self.performance = {
            "total_profit": 0.0,
            "total_trades": 0,
            "win_trades": 0,
            "loss_trades": 0,
            "win_rate": 0.0,
            "max_drawdown": 0.0,
            "current_drawdown": 0.0
        }
        self.positions = []
        self.trades = []
        self.logs = []
    
    def update_status(self, status: str, error_message: str = ""):
        """
        更新策略状态
        
        参数:
            status (str): 策略状态
            error_message (str, optional): 错误信息
        """
        self.status = status
        self.error_message = error_message
        self.last_update_time = datetime.now()
    
    def update_performance(self, performance: Dict[str, Any]):
        """
        更新策略绩效
        
        参数:
            performance (Dict[str, Any]): 策略绩效
        """
        self.performance.update(performance)
        self.last_update_time = datetime.now()
    
    def update_positions(self, positions: List[Dict[str, Any]]):
        """
        更新策略持仓
        
        参数:
            positions (List[Dict[str, Any]]): 策略持仓
        """
        self.positions = positions
        self.last_update_time = datetime.now()
    
    def update_trades(self, trades: List[Dict[str, Any]]):
        """
        更新策略交易记录
        
        参数:
            trades (List[Dict[str, Any]]): 策略交易记录
        """
        self.trades = trades
        self.last_update_time = datetime.now()
    
    def add_log(self, log: str):
        """
        添加策略日志
        
        参数:
            log (str): 策略日志
        """
        self.logs.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": log
        })
        self.last_update_time = datetime.now()
        
        # 只保留最近100条日志
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        返回:
            Dict[str, Any]: 策略监控信息
        """
        return {
            "strategy_name": self.strategy_name,
            "user_strategy_id": self.user_strategy_id,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_update_time": self.last_update_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
            "error_message": self.error_message,
            "performance": self.performance,
            "positions": self.positions,
            "trades": self.trades,
            "logs": self.logs
        }

class MonitorService:
    """策略监控服务"""
    
    def __init__(self, main_engine: STMainEngine):
        """
        初始化
        
        参数:
            main_engine (STMainEngine): 主引擎实例
        """
        self.main_engine = main_engine
        self.cta_engine = main_engine.get_cta_engine()
        self.monitors: Dict[int, StrategyMonitor] = {}  # user_strategy_id -> StrategyMonitor
        self.running = False
        self.monitor_thread = None
    
    def start_monitor(self, user_strategy_id: int, strategy_name: str) -> bool:
        """
        开始监控策略
        
        参数:
            user_strategy_id (int): 用户策略ID
            strategy_name (str): 策略名称
            
        返回:
            bool: 是否成功
        """
        if user_strategy_id in self.monitors:
            logger.warning(f"策略 {strategy_name} 已经在监控中")
            return False
        
        # 创建策略监控
        monitor = StrategyMonitor(strategy_name, user_strategy_id)
        self.monitors[user_strategy_id] = monitor
        
        logger.info(f"开始监控策略 {strategy_name}")
        return True
    
    def stop_monitor(self, user_strategy_id: int) -> bool:
        """
        停止监控策略
        
        参数:
            user_strategy_id (int): 用户策略ID
            
        返回:
            bool: 是否成功
        """
        if user_strategy_id not in self.monitors:
            logger.warning(f"策略 {user_strategy_id} 不在监控中")
            return False
        
        # 移除策略监控
        monitor = self.monitors.pop(user_strategy_id)
        
        logger.info(f"停止监控策略 {monitor.strategy_name}")
        return True
    
    def get_monitor(self, user_strategy_id: int) -> Optional[StrategyMonitor]:
        """
        获取策略监控
        
        参数:
            user_strategy_id (int): 用户策略ID
            
        返回:
            Optional[StrategyMonitor]: 策略监控
        """
        return self.monitors.get(user_strategy_id)
    
    def get_all_monitors(self) -> List[Dict[str, Any]]:
        """
        获取所有策略监控
        
        返回:
            List[Dict[str, Any]]: 策略监控列表
        """
        return [monitor.to_dict() for monitor in self.monitors.values()]
    
    def start(self):
        """启动监控服务"""
        if self.running:
            logger.warning("监控服务已经在运行中")
            return
        
        self.running = True
        self.monitor_thread = Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("监控服务已启动")
    
    def stop(self):
        """停止监控服务"""
        if not self.running:
            logger.warning("监控服务未在运行")
            return
        
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
            self.monitor_thread = None
        
        logger.info("监控服务已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                self._update_monitors()
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
            
            # 每5秒更新一次
            time.sleep(5)
    
    def _update_monitors(self):
        """更新所有策略监控"""
        # 获取所有策略状态
        strategy_infos = self.cta_engine.get_all_strategy_class_names()
        strategy_status = {}
        
        for strategy_name in strategy_infos:
            # 获取策略状态
            status = self.cta_engine.get_strategy_status(strategy_name)
            strategy_status[strategy_name] = status
        
        # 更新监控状态
        for user_strategy_id, monitor in list(self.monitors.items()):
            strategy_name = monitor.strategy_name
            
            # 检查策略是否存在
            if strategy_name not in strategy_status:
                monitor.update_status("error", "策略不存在")
                continue
            
            # 更新策略状态
            status = strategy_status[strategy_name]
            if status:
                monitor.update_status("running")
                
                # 获取策略实例
                strategy = self.cta_engine.strategies.get(strategy_name)
                if strategy:
                    # 更新策略绩效
                    performance = {
                        "total_profit": getattr(strategy, "total_profit", 0.0),
                        "total_trades": getattr(strategy, "total_trades", 0),
                        "win_trades": getattr(strategy, "win_trades", 0),
                        "loss_trades": getattr(strategy, "loss_trades", 0),
                        "win_rate": getattr(strategy, "win_rate", 0.0),
                        "max_drawdown": getattr(strategy, "max_drawdown", 0.0),
                        "current_drawdown": getattr(strategy, "current_drawdown", 0.0)
                    }
                    monitor.update_performance(performance)
                    
                    # 更新策略持仓
                    positions = []
                    pos = getattr(strategy, "pos", 0)
                    if pos != 0:
                        positions.append({
                            "symbol": getattr(strategy, "vt_symbol", ""),
                            "direction": "多" if pos > 0 else "空",
                            "volume": abs(pos)
                        })
                    monitor.update_positions(positions)
                    
                    # 更新策略交易记录
                    trades = getattr(strategy, "trades", [])
                    trade_list = []
                    for trade in trades[-10:]:  # 只取最近10条
                        trade_list.append({
                            "time": trade.time.strftime("%Y-%m-%d %H:%M:%S"),
                            "symbol": trade.vt_symbol,
                            "direction": trade.direction.value,
                            "offset": trade.offset.value,
                            "price": trade.price,
                            "volume": trade.volume
                        })
                    monitor.update_trades(trade_list)
            else:
                monitor.update_status("stopped")
