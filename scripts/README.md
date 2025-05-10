# 回测 API 修复脚本

这个目录包含了修复回测 API 的脚本。

## 问题描述

回测报告 API (`/api/strategies/backtest/reports/{backtest_id}`) 返回 404 错误，原因是 `BacktestRecord` 模型缺少以下字段：

- `strategy_name`: 策略名称
- `statistics`: 统计数据 (JSON)

这导致了以下错误：

```
AttributeError: 'BacktestRecord' object has no attribute 'strategy_name'. Did you mean: 'strategy_id'?
```

```
AttributeError: 'BacktestRecord' object has no attribute 'statistics'
```

## 解决方案

1. 添加缺失的字段到 `BacktestRecord` 表
2. 修改 `get_backtest_report_data` 函数，使其能够处理缺失的字段

## 使用方法

### 1. 运行修复脚本

```bash
python scripts/fix_backtest_api.py
```

这个脚本会：

1. 添加缺失的字段到 `BacktestRecord` 表
2. 替换 `get_backtest_report_data` 函数，使其能够处理缺失的字段

### 2. 重启后端服务

```bash
# 停止当前的后端服务
# 然后重新启动
python -m simpletrade.main
```

## 脚本说明

- `add_missing_fields.py`: 添加缺失的字段到 `BacktestRecord` 表
- `fix_backtest_api.py`: 运行添加缺失字段的脚本，并替换 `get_backtest_report_data` 函数
- `service.py.fixed`: 修复后的 `service.py` 文件，包含了能够处理缺失字段的 `get_backtest_report_data` 函数

## 注意事项

- 这些脚本会修改数据库结构和后端代码，请在运行前备份数据库和代码
- 如果脚本运行失败，可以手动执行以下步骤：
  1. 运行 `python scripts/add_missing_fields.py` 添加缺失的字段
  2. 将 `simpletrade/apps/st_backtest/service.py.fixed` 复制到 `simpletrade/apps/st_backtest/service.py`
- 如果需要恢复原始代码，可以将 `simpletrade/apps/st_backtest/service.py.bak` 复制回 `simpletrade/apps/st_backtest/service.py`
