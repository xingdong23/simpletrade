#!/bin/bash

# 运行回测脚本
# 用法: ./run_backtest.sh <策略名称> <开始日期> <结束日期> <交易品种> <交易所>

# 检查参数
if [ $# -lt 5 ]; then
    echo "用法: $0 <策略名称> <开始日期> <结束日期> <交易品种> <交易所>"
    echo "示例: $0 MovingAverageStrategy 20200101 20201231 BTCUSDT BINANCE"
    exit 1
fi

STRATEGY=$1
START_DATE=$2
END_DATE=$3
SYMBOL=$4
EXCHANGE=$5

echo "开始回测..."
echo "策略: $STRATEGY"
echo "时间范围: $START_DATE - $END_DATE"
echo "交易品种: $SYMBOL"
echo "交易所: $EXCHANGE"

# 运行回测
python -m simpletrade.backtest.run_backtest \
    --strategy $STRATEGY \
    --start_date $START_DATE \
    --end_date $END_DATE \
    --symbol $SYMBOL \
    --exchange $EXCHANGE

echo "回测完成!"
