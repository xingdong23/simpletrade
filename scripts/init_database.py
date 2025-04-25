"""
数据库初始化脚本

创建数据库表并添加示例数据。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

import pymysql
from simpletrade.config.database import init_db, get_db, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from simpletrade.models.database import Symbol, Strategy, UserStrategy, BacktestRecord

def create_database():
    """创建数据库"""
    try:
        # 连接MySQL服务器
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=int(DB_PORT)
        )
        
        # 创建游标
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        print(f"数据库 {DB_NAME} 创建成功或已存在")
        
        # 关闭连接
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        sys.exit(1)

def add_sample_data():
    """添加示例数据"""
    db = next(get_db())  # 获取数据库会话
    try:
        # 添加交易品种
        symbols = [
            Symbol(symbol="AAPL", exchange="SMART", name="Apple Inc.", category="Stock"),
            Symbol(symbol="MSFT", exchange="SMART", name="Microsoft Corporation", category="Stock"),
            Symbol(symbol="GOOG", exchange="SMART", name="Alphabet Inc.", category="Stock"),
            Symbol(symbol="AMZN", exchange="SMART", name="Amazon.com, Inc.", category="Stock"),
            Symbol(symbol="FB", exchange="SMART", name="Meta Platforms, Inc.", category="Stock"),
            Symbol(symbol="TSLA", exchange="SMART", name="Tesla, Inc.", category="Stock"),
            Symbol(symbol="NVDA", exchange="SMART", name="NVIDIA Corporation", category="Stock"),
            Symbol(symbol="JPM", exchange="SMART", name="JPMorgan Chase & Co.", category="Stock"),
            Symbol(symbol="V", exchange="SMART", name="Visa Inc.", category="Stock"),
            Symbol(symbol="JNJ", exchange="SMART", name="Johnson & Johnson", category="Stock")
        ]
        db.add_all(symbols)
        
        # 添加策略
        strategies = [
            Strategy(
                name="双均线交叉策略",
                description="使用短期和长期移动平均线的交叉来产生交易信号。当短期均线上穿长期均线时买入，当短期均线下穿长期均线时卖出。",
                category="趋势跟踪",
                type="basic",
                complexity=1,
                resource_requirement=1,
                parameters={
                    "fast_window": {"type": "int", "default": 5, "min": 2, "max": 20, "description": "短期均线周期"},
                    "slow_window": {"type": "int", "default": 20, "min": 5, "max": 60, "description": "长期均线周期"}
                }
            ),
            Strategy(
                name="RSI超买超卖策略",
                description="使用相对强弱指数(RSI)来识别超买和超卖条件。当RSI低于超卖阈值时买入，当RSI高于超买阈值时卖出。",
                category="震荡指标",
                type="basic",
                complexity=2,
                resource_requirement=1,
                parameters={
                    "rsi_window": {"type": "int", "default": 14, "min": 5, "max": 30, "description": "RSI计算周期"},
                    "oversold": {"type": "int", "default": 30, "min": 10, "max": 40, "description": "超卖阈值"},
                    "overbought": {"type": "int", "default": 70, "min": 60, "max": 90, "description": "超买阈值"}
                }
            ),
            Strategy(
                name="布林带突破策略",
                description="使用布林带来识别价格突破。当价格突破上轨时买入，当价格突破下轨时卖出。",
                category="波动性",
                type="basic",
                complexity=2,
                resource_requirement=2,
                parameters={
                    "window": {"type": "int", "default": 20, "min": 10, "max": 50, "description": "布林带周期"},
                    "dev": {"type": "float", "default": 2.0, "min": 1.0, "max": 3.0, "description": "标准差倍数"}
                }
            ),
            Strategy(
                name="MACD策略",
                description="使用MACD指标来产生交易信号。当MACD线上穿信号线时买入，当MACD线下穿信号线时卖出。",
                category="趋势跟踪",
                type="basic",
                complexity=3,
                resource_requirement=2,
                parameters={
                    "fast_window": {"type": "int", "default": 12, "min": 5, "max": 20, "description": "快线周期"},
                    "slow_window": {"type": "int", "default": 26, "min": 15, "max": 40, "description": "慢线周期"},
                    "signal_window": {"type": "int", "default": 9, "min": 5, "max": 15, "description": "信号线周期"}
                }
            ),
            Strategy(
                name="KDJ策略",
                description="使用KDJ指标来产生交易信号。当K线上穿D线时买入，当K线下穿D线时卖出。",
                category="震荡指标",
                type="basic",
                complexity=3,
                resource_requirement=2,
                parameters={
                    "k_period": {"type": "int", "default": 9, "min": 5, "max": 20, "description": "K线周期"},
                    "d_period": {"type": "int", "default": 3, "min": 2, "max": 10, "description": "D线周期"},
                    "j_period": {"type": "int", "default": 3, "min": 2, "max": 10, "description": "J线周期"}
                }
            ),
            Strategy(
                name="多因子选股策略",
                description="使用多个因子（如市盈率、市净率、ROE等）来选择股票。根据因子得分对股票进行排名，选择得分最高的股票进行投资。",
                category="选股",
                type="advanced",
                complexity=4,
                resource_requirement=3,
                parameters={
                    "factors": {"type": "array", "default": ["pe", "pb", "roe"], "description": "选股因子"},
                    "weights": {"type": "array", "default": [0.4, 0.3, 0.3], "description": "因子权重"},
                    "top_n": {"type": "int", "default": 10, "min": 5, "max": 50, "description": "选择的股票数量"}
                }
            ),
            Strategy(
                name="机器学习预测策略",
                description="使用机器学习模型（如随机森林、LSTM等）来预测股票价格走势，并根据预测结果产生交易信号。",
                category="AI",
                type="advanced",
                complexity=5,
                resource_requirement=5,
                parameters={
                    "model_type": {"type": "string", "default": "random_forest", "options": ["random_forest", "lstm", "xgboost"], "description": "模型类型"},
                    "features": {"type": "array", "default": ["close", "volume", "ma5", "ma10", "rsi"], "description": "特征"},
                    "lookback": {"type": "int", "default": 20, "min": 5, "max": 60, "description": "回溯周期"},
                    "prediction_horizon": {"type": "int", "default": 5, "min": 1, "max": 20, "description": "预测周期"}
                }
            )
        ]
        db.add_all(strategies)
        
        db.commit()  # 确保提交事务
        print("示例数据添加成功")
    finally:
        db.close()  # 确保关闭会话

def main():
    """主函数"""
    print("开始初始化数据库...")
    
    # 创建数据库
    create_database()
    
    # 创建表
    init_db()
    print("数据库表创建成功")
    
    # 添加示例数据
    add_sample_data()
    
    print("数据库初始化完成")

if __name__ == "__main__":
    main()
