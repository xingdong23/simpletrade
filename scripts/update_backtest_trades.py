#!/usr/bin/env python
"""
更新回测记录的交易详情

这个脚本会重新运行指定的回测，并将交易详情更新到数据库中。
"""

import sys
import os
from pathlib import Path
import logging
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from simpletrade.config.database import SessionLocal
from simpletrade.models.database import BacktestRecord, Strategy
from simpletrade.apps.st_backtest.service import BacktestService

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_backtest_trades(backtest_id: str):
    """更新指定回测记录的交易详情"""
    db = SessionLocal()
    try:
        # 获取回测记录
        record = db.query(BacktestRecord).filter(BacktestRecord.id == backtest_id).first()
        if not record:
            logger.error(f"未找到ID为 {backtest_id} 的回测记录")
            return False
        
        logger.info(f"找到回测记录: ID={record.id}, 策略ID={record.strategy_id}, 符号={record.symbol}")
        
        # 创建回测服务
        backtest_service = BacktestService()
        
        # 重新运行回测
        result = backtest_service.run_backtest(
            strategy_id=record.strategy_id,
            symbol=record.symbol,
            exchange=record.exchange,
            interval=record.interval,
            start_date=record.start_date,
            end_date=record.end_date,
            initial_capital=float(record.initial_capital),
            rate=float(record.rate) if hasattr(record, 'rate') and record.rate else 0.0001,
            slippage=float(record.slippage) if hasattr(record, 'slippage') and record.slippage else 0,
            parameters=json.loads(record.parameters) if hasattr(record, 'parameters') and record.parameters else None,
            user_id=None  # 不保存新的回测记录
        )
        
        # 提取交易记录
        trades = result.get("trades", [])
        logger.info(f"获取到 {len(trades)} 条交易记录")
        
        # 更新回测记录
        record.trades_json = json.dumps(trades)
        db.commit()
        
        logger.info(f"成功更新回测记录 {backtest_id} 的交易详情")
        return True
    except Exception as e:
        logger.error(f"更新回测记录 {backtest_id} 的交易详情时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def update_all_backtest_trades():
    """更新所有回测记录的交易详情"""
    db = SessionLocal()
    try:
        # 获取所有回测记录
        records = db.query(BacktestRecord).all()
        logger.info(f"找到 {len(records)} 条回测记录")
        
        success_count = 0
        for record in records:
            try:
                if update_backtest_trades(str(record.id)):
                    success_count += 1
            except Exception as e:
                logger.error(f"更新回测记录 {record.id} 时出错: {e}")
        
        logger.info(f"成功更新 {success_count}/{len(records)} 条回测记录的交易详情")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="更新回测记录的交易详情")
    parser.add_argument("--id", help="要更新的回测记录ID，如果不指定则更新所有记录")
    
    args = parser.parse_args()
    
    if args.id:
        update_backtest_trades(args.id)
    else:
        update_all_backtest_trades()
