# 数据同步服务测试说明

## 测试文件概述

本目录包含对`DataSyncService`的单元测试，用于验证数据同步服务的各项功能。测试覆盖了以下场景：

### 单元测试 (`test_data_sync_service.py`)

1. **首次导入场景**：验证当`DataImportLog`中没有某个目标的记录时，服务能否从配置的默认起始日期开始，成功导入数据直到昨天。

2. **增量更新场景**：验证当`DataImportLog`中已有记录，且上次导入日期早于昨天时，服务能否只导入从`last_import_date + 1 day`到昨天的新数据。

3. **数据已是最新场景**：验证当`DataImportLog`中上次导入日期已经是昨天或更晚时，服务能否正确识别并跳过导入。

4. **Qlib数据源特定场景**：验证对于Qlib目标，服务能否正确找到Qlib数据目录（`cn_data`或`us_data`）。

5. **QlibDataImporter数据转换**：验证`QlibDataImporter`能否正确处理Qlib数据格式并转换为`BarData`列表。

6. **数据库保存**：验证转换后的`BarData`能否成功通过`database_manager.save_bar_data`保存到VnPy的数据库。

7. **无效配置**：验证如果配置无效（缺少字段），服务能否跳过该目标并记录错误。

8. **Qlib目录不存在**：验证如果Qlib目录不存在，服务能否记录错误并标记该目标为失败。

9. **数据库错误**：验证如果数据库连接失败或`save_bar_data`出错，服务能否捕获异常、记录错误并标记该目标为失败。

### 集成测试 (`../integration/test_data_sync_integration.py`)

1. **端到端测试**：验证从Qlib数据源导入数据到数据库的完整流程。

2. **QlibDataImporter与模拟数据**：使用模拟的Qlib数据测试QlibDataImporter的功能。

## 运行测试

### 运行单元测试

```bash
python -m unittest tests/unit/test_data_sync_service.py
```

### 运行集成测试

注意：集成测试需要实际的数据库连接，默认被跳过。在集成测试环境中运行时，请移除`@unittest.skip`装饰器。

```bash
python -m unittest tests/integration/test_data_sync_integration.py
```

## 测试依赖

- 单元测试使用模拟对象（Mock）来隔离依赖，不需要实际的数据库连接。
- 集成测试需要实际的数据库连接和Qlib数据目录结构。