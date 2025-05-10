-- 添加缺失的字段到 backtest_records 表
ALTER TABLE backtest_records ADD COLUMN strategy_name VARCHAR(100);
ALTER TABLE backtest_records ADD COLUMN strategy_class_name VARCHAR(100);
ALTER TABLE backtest_records ADD COLUMN statistics TEXT;
ALTER TABLE backtest_records ADD COLUMN parameters TEXT;
ALTER TABLE backtest_records ADD COLUMN daily_results_json TEXT;
ALTER TABLE backtest_records ADD COLUMN trades_json TEXT;
ALTER TABLE backtest_records ADD COLUMN capital VARCHAR(20);
ALTER TABLE backtest_records ADD COLUMN rate VARCHAR(20);
ALTER TABLE backtest_records ADD COLUMN slippage VARCHAR(20);
ALTER TABLE backtest_records ADD COLUMN mode VARCHAR(20);
ALTER TABLE backtest_records ADD COLUMN ran_at DATETIME;
