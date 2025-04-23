# Data Import Module Status Summary

## 2024-07-28

**Goal:** Implement automatic historical data synchronization (from Qlib initially) at API startup using a background thread, **ultimately saving the data to the MySQL database via VnPy's database manager.**

**Problem Encountered:** The core issue is the **inability to successfully save synchronized data to the MySQL database.** This is manifesting as the background thread (`run_initial_data_sync` in `data_sync_service.py`), responsible for the synchronization and saving process, failing silently after starting. While the thread entry point is reached, subsequent operations, crucially including the database initialization (`get_database()`) and the data saving step (`save_bar_data`), do not complete or log any output (even with `print` statements), preventing data persistence.

**Troubleshooting Steps & Findings:**

1.  **Logging Issues:** Suspected and partially mitigated issues with logging in the startup thread by replacing `logger` with `print`.
2.  **Database Initialization/Configuration:** Focused on ensuring `vnpy.trader.database.get_database()` could initialize the MySQL connection correctly within the background thread.
    *   **Method 1 (`vt_setting.json`):** Failed due to container filesystem permissions.
    *   **Method 2 (Environment Variables):** Implemented setting `VNPY_DATABASE_*` environment variables in `run_api.py` *before* VnPy imports, as the current likely working configuration method.
3.  **Code Adjustments:**
    *   Modified `run_api.py` to set environment variables.
    *   Modified `data_sync_service.py` to use `get_database()` (expecting it to read env vars) and kept `print` for debugging.

**Current Status:**

*   Code modifications to use environment variables for database configuration and `get_database()` are complete.
*   The immediate next step is to verify if this configuration method allows the background thread to **successfully initialize the MySQL database connection** via `get_database()`.
*   **Crucially, even if `get_database()` succeeds, the subsequent step of calling `self.db.save_bar_data(bars)` within `_import_data_from_qlib` needs to be verified.** It's possible that even with a successful connection, the save operation itself might fail for other reasons (data format issues, table schema mismatches, transaction problems, etc.) which haven't been observable yet due to the earlier initialization failures.
*   Awaiting service restart and log analysis to check:
    *   Confirmation that environment variables are set.
    *   Successful return of a `MysqlDatabase` instance from `get_database()` in the thread.
    *   Progress of the `sync_target` and specifically the `_import_data_from_qlib` function, looking for `print` statements around the `save_bar_data` call.

**Next Step:** Restart the service and meticulously analyze the startup logs provided by the `print` statements, focusing on database initialization and the data saving attempt.

## 数据导入功能状态摘要 (截至 2025-04-22)

## 当前状态

*   **目标:** 实现一个健壮的数据同步服务 (`DataSyncService`)，能够从不同的数据源（目前主要是 Qlib）导入历史 K 线数据到 VnPy 的数据库（例如 MySQL）中。
*   **已完成:**
    *   `DataSyncService` 的基本框架已搭建在 `simpletrade/data_sync/service.py` 中。
    *   服务可以通过 `run_data_sync.py` 启动。
    *   定义了 `DATA_SYNC_TARGETS` 配置结构，用于指定要同步的数据目标（代码、交易所、周期、来源等）。
    *   初步实现了 `QlibDataImporter`，用于从 Qlib 数据目录加载数据。
    *   服务能够读取 `DATA_SYNC_TARGETS` 并为每个目标调用 `sync_target` 方法。
    *   `sync_target` 方法包含基本的逻辑：
        *   检查 `DataImportLog` 以确定上次导入日期。
        *   计算需要导入的日期范围（从上次导入日期+1天 或 默认起始日期 到 昨天）。
        *   根据数据源调用相应的导入器（目前仅 `QlibDataImporter`）。
        *   调用 `database_manager.save_bar_data` 保存数据。
        *   更新 `DataImportLog`。
*   **进行中/待办:**
    *   **定义和实现数据导入测试用例 (当前焦点)**。
    *   验证和完善 `QlibDataImporter` 的数据加载和转换逻辑。
    *   验证 `database_manager.save_bar_data` 是否能正确将 `BarData` 保存到目标数据库。
    *   实现对其他数据源（如 CSV、API 等）的支持（如果需要）。
    *   细化和配置化数据同步的起始和结束日期逻辑。
    *   增强错误处理和日志记录。
    *   添加必要的单元测试和集成测试。
*   **已知问题/风险:**
    *   `QlibDataImporter` 的实现尚未经过充分测试，特别是与 `database_manager` 的交互。
    *   错误处理机制比较基础，需要增强。
    *   日志记录可能需要更详细的信息以方便调试。
    *   启动日志似乎有重复输出的问题（可能与 Uvicorn 或 Docker 配置有关）。
    *   VnPy 数据服务未配置的警告信息需要确认是否影响回测。

## 建议的后续步骤

1.  **定义数据导入测试用例:** 优先明确和编写具体的数据导入测试场景，这将指导后续数据导入和回测功能的具体实现和验证。
2.  **验证/完成 Qlib 导入逻辑:** (在测试用例明确后进行)
    *   确保 `QlibDataImporter.import_data` 能正确处理提供的 `qlib_dir`、代码、交易所、周期和日期范围。
    *   确认返回的 `BarData` 对象格式正确。
    *   彻底测试 `database_manager.save_bar_data(bars_to_save)` 调用。`database_module.get_database()` 是否返回了为目标数据库（例如 MySQL）配置的正确管理器实例？`save_bar_data` 是否按预期工作？
    *   手动清除或调整 `DataImportLog` 条目以进行测试，强制执行导入逻辑。
3.  **实现其他数据源:** 如果需要，在 `sync_target` 中添加逻辑块（例如 `elif source == "csv":`），并实现相应的导入器类（例如 `CsvImporter`）。
4.  **细化同步日期逻辑:**
    *   使默认起始日期（`datetime(2010, 1, 1)`）可配置，可能按目标配置。
    *   检查结束日期逻辑（目前是昨天）是否总是合适的。
5.  **错误处理与重试:** 在 `sync_target` 中实现更健壮的错误处理机制，并可能为临时性故障（例如获取数据时的网络问题）添加重试逻辑。
6.  **调查日志重复问题:** 查找启动日志出现重复的原因。是 Docker Compose 配置问题、脚本执行问题还是 Uvicorn 的行为？
7.  **处理 VnPy 数据服务警告:** 确定是否需要处理"没有配置要使用的数据服务..."的警告。如果回测数据完全依赖 `database_manager`，这可能无害。如果 VnPy 的其他部分期望有配置好的数据接口，则研究在 `run_api.py` 或配置文件中适当设置 `VNPY_SETTINGS['datafeed.name']` 及相关选项。