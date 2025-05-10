#!/usr/bin/env python
"""
数据库迁移脚本：添加缺失的字段到 BacktestRecord 表

这个脚本会添加以下字段到 BacktestRecord 表：
- strategy_name: 策略名称
- strategy_class_name: 策略类名
- statistics: 统计数据 (JSON)
- parameters: 参数 (JSON)
- daily_results_json: 每日结果 (JSON)
- trades_json: 交易记录 (JSON)
- capital: 初始资金
- rate: 手续费率
- slippage: 滑点
- mode: 回测模式
- ran_at: 执行时间
"""

import sys
import os
from pathlib import Path
import logging
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from sqlalchemy import Column, String, DateTime, Text, inspect
from sqlalchemy.sql import func

from simpletrade.config.database import engine, SessionLocal
from simpletrade.models.database import BacktestRecord

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_column(engine, table_name, column):
    """添加列到表中"""
    column_name = column.name
    column_type = column.type.compile(engine.dialect)
    
    try:
        engine.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}')
        logger.info(f"添加列 {column_name} 到表 {table_name} 成功")
    except Exception as e:
        logger.error(f"添加列 {column_name} 到表 {table_name} 失败: {str(e)}")
        logger.debug(traceback.format_exc())

def main():
    """主函数"""
    logger.info("开始添加缺失的字段到 BacktestRecord 表")
    
    # 获取表的当前列
    inspector = inspect(engine)
    columns = [column['name'] for column in inspector.get_columns('backtest_records')]
    
    # 定义要添加的列
    new_columns = {
        'strategy_name': Column('strategy_name', String(100)),
        'strategy_class_name': Column('strategy_class_name', String(100)),
        'statistics': Column('statistics', Text),
        'parameters': Column('parameters', Text),
        'daily_results_json': Column('daily_results_json', Text),
        'trades_json': Column('trades_json', Text),
        'capital': Column('capital', String(20)),
        'rate': Column('rate', String(20)),
        'slippage': Column('slippage', String(20)),
        'mode': Column('mode', String(20)),
        'ran_at': Column('ran_at', DateTime, server_default=func.now())
    }
    
    # 添加缺失的列
    for column_name, column in new_columns.items():
        if column_name not in columns:
            add_column(engine, 'backtest_records', column)
        else:
            logger.info(f"列 {column_name} 已存在于表 backtest_records 中")
    
    # 更新现有记录
    with SessionLocal() as session:
        records = session.query(BacktestRecord).all()
        for record in records:
            if not hasattr(record, 'strategy_name') or not record.strategy_name:
                # 从 Strategy 表中获取策略名称
                try:
                    strategy = session.query('name').filter_by(id=record.strategy_id).first()
                    if strategy:
                        record.strategy_name = strategy.name
                    else:
                        record.strategy_name = f"Strategy {record.strategy_id}"
                except:
                    record.strategy_name = f"Strategy {record.strategy_id}"
            
            if not hasattr(record, 'strategy_class_name') or not record.strategy_class_name:
                record.strategy_class_name = "Unknown"
            
            if not hasattr(record, 'statistics') or not record.statistics:
                if hasattr(record, 'results') and record.results and 'statistics' in record.results:
                    record.statistics = str(record.results['statistics'])
                else:
                    record.statistics = "{}"
            
            if not hasattr(record, 'parameters') or not record.parameters:
                if hasattr(record, 'results') and record.results and 'parameters' in record.results:
                    record.parameters = str(record.results['parameters'])
                else:
                    record.parameters = "{}"
            
            if not hasattr(record, 'daily_results_json') or not record.daily_results_json:
                record.daily_results_json = "[]"
            
            if not hasattr(record, 'trades_json') or not record.trades_json:
                record.trades_json = "[]"
            
            if not hasattr(record, 'capital') or not record.capital:
                record.capital = str(record.initial_capital)
            
            if not hasattr(record, 'rate') or not record.rate:
                record.rate = "0.0001"
            
            if not hasattr(record, 'slippage') or not record.slippage:
                record.slippage = "0"
            
            if not hasattr(record, 'mode') or not record.mode:
                record.mode = "bar"
            
            if not hasattr(record, 'ran_at') or not record.ran_at:
                record.ran_at = datetime.now()
        
        session.commit()
        logger.info(f"更新了 {len(records)} 条记录")
    
    logger.info("添加缺失的字段到 BacktestRecord 表完成")

if __name__ == "__main__":
    main()
