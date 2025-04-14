# SimpleTrade 启动指南

本文档提供了启动 SimpleTrade 应用的正确方法，包括后端 API 服务和前端 Web 界面。

## 环境准备

确保您已经激活了 SimpleTrade 的 conda 环境：

```bash
conda activate simpletrade
```

## 启动后端 API 服务

在项目根目录下执行以下命令启动后端 API 服务：

```bash
# 方式1：如果已经激活了 simpletrade 环境（更简单，始终显示输出）
python -m uvicorn simpletrade.api.server:app --host 0.0.0.0 --port 8002 --reload

# 方式2：使用 conda run 命令（不需要先激活环境，更一致的环境设置）
conda run -n simpletrade python -m uvicorn simpletrade.api.server:app --host 0.0.0.0 --port 8002 --reload

# 如果使用方式2看不到输出，可以添加 --no-capture-output 参数
conda run --no-capture-output -n simpletrade python -m uvicorn simpletrade.api.server:app --host 0.0.0.0 --port 8002 --reload
```

参数说明：
- `--host 0.0.0.0`：允许从任何 IP 地址访问 API 服务
- `--port 8002`：API 服务监听的端口（避免与其他服务的端口冲突）
- `--reload`：当代码变更时自动重新加载服务（开发模式）

启动成功后，可以通过访问 http://localhost:8002/docs 查看 API 文档。

### 注意事项

1. **使用 conda run 命令**：强烈推荐使用 `conda run -n simpletrade` 命令启动服务，而不是直接使用 `python -m uvicorn`。这是因为：
   - `conda run` 命令会创建一个完全隔离的环境，确保所有环境变量和路径设置都是正确的
   - 即使已经激活了 simpletrade 环境，直接使用 `python` 命令仍可能遇到环境变量或导入路径问题
   - 实际测试表明，`conda run` 命令更可靠，可以避免各种导入错误

2. **确保已安装依赖**：在启动服务前，确保已经安装了所有必要的依赖，包括 TA-Lib 和 vnpy。

3. **开发模式安装**：强烈建议使用开发模式安装 SimpleTrade（`pip install -e .`），以避免模块导入错误。

4. **端口冲突**：如果端口 8002 已被占用，可以尝试其他端口，如 8003、8004 等。

5. **常见错误及解决方法**：
   - `name 'ApiResponseModel' is not defined` 错误：这是一个命名错误，已修复。如果仍然出现，请将 `simpletrade/api/wechat/data.py` 文件中的 `ApiResponseModel` 改为 `ApiResponse`
   - `STBaseApp.__init__() missing required arguments` 错误：这是一个初始化错误，但不影响服务的基本功能。确保使用开发模式安装了 SimpleTrade
   - `symbol not found in flat namespace '_TA_ACCBANDS'` 错误：重新安装 TA-Lib（参见安装指南）
   - `vnpy_datamanager not found` 等警告：这些是警告，表明某些 vnpy 组件没有安装。如果您不需要这些功能，可以暂时忽略

6. **conda run 命令输出问题**：
   - `conda run` 命令默认会捕获所有输出，导致用户看不到日志
   - 添加 `--no-capture-output` 参数可以显示完整输出：`conda run --no-capture-output -n simpletrade ...`
   - 如果不确定服务是否启动，可以尝试访问 API：`curl http://localhost:8002/api/test/hello`
   - 或者在浏览器中访问：http://localhost:8002/docs

### Python -m 命令的原理

在启动服务时，我们使用 `python -m uvicorn` 命令。这个命令的工作原理值得理解：

1. **模块执行机制**：
   - `python -m module_name` 会将指定的模块作为脚本执行
   - Python 会在 `sys.path` 中查找该模块，导入并执行它

2. **导入路径影响**：
   - 当前工作目录会被添加到 `sys.path` 的开头
   - 这意味着当前目录结构对模块导入至关重要

3. **相对导入支持**：
   - `python -m` 命令支持相对导入（如 `from . import module`）
   - 这对于复杂的包结构非常重要

4. **两种启动方式的比较**：
   - **直接使用 `python -m`**：
     - 更简单，不需要额外的参数
     - 始终显示输出，方便调试
     - 需要先激活 conda 环境
   - **使用 `conda run -n simpletrade`**：
     - 创建一个完全隔离的环境
     - 确保所有环境变量和导入路径都正确设置
     - 不需要先激活环境
     - 默认不显示输出，需要添加 `--no-capture-output` 参数

5. **常见错误原因**：
   - 如果项目没有以开发模式安装（`pip install -e .`），可能会出现模块找不到的错误
   - 如果依赖库（如 TA-Lib）安装不正确，可能会出现符号加载错误
   - 如果代码中有命名错误（如 `ApiResponseModel`），需要修正这些错误

在正确设置环境并修复代码错误后，两种启动方式都可以正常工作。您可以根据个人偏好选择使用哪种方式。

### 测试 API 服务器

如果您遇到了依赖问题，可以使用测试 API 服务器，该服务器不依赖于 talib 和 vnpy：

```bash
python scripts/test_api_server.py
```

测试服务器将在端口 8000 上运行，并提供基本的 API 路由。

## 启动前端 Web 界面

在项目根目录下的 `web-frontend` 目录中执行以下命令启动前端 Web 界面：

```bash
cd web-frontend
npm run serve
```

启动成功后，通常可以通过访问 http://localhost:8080 查看前端界面。

### 前端技术栈

前端使用以下技术栈：

- Vue 2.x：前端 JavaScript 框架
- Element UI：基于 Vue 的组件库，提供了丰富的 UI 组件
- ECharts：数据可视化图表库
- Vue Router：前端路由管理
- Vuex：状态管理

前端包含以下主要页面：

- 策略中心：管理和配置交易策略
- 交易中心：查看账户信息、持仓和订单
- AI分析：市场分析、股票预测和模型训练
- 用户中心：管理个人资料、账户设置和订阅

## 验证 vnpy_tiger 加载状态

要验证 `vnpy_tiger` 是否成功加载，可以查看后端 API 服务的启动日志。

首先，`main.py` 在启动时应该会打印类似以下的日志，表示 `vendors` 目录已添加到 `sys.path`：
```
[INFO] Added vendors path to sys.path: /path/to/your/project/vendors
```

然后，如果 `vnpy_tiger` 及其依赖（如 `tigeropen`）都正常，你应该会看到日志中包含：
```
Attempting to import vnpy_tiger...
vnpy_tiger imported successfully.
Global: Tiger Gateway registered.
```

如果导入失败 (看到 `Warning: vnpy_tiger not found. Error: ...`)，或者没有看到 `Tiger Gateway registered.`，请检查：

1. 确认 `vendors/vnpy_tiger` 目录及其内容存在。
2. 确认 `main.py` 开头的 `sys.path` 修改被执行且路径正确。
3. 确认 `vnpy_tiger` 的依赖已安装：
   ```bash
   conda activate simpletrade
   pip show tigeropen # 检查 tigeropen 是否安装
   # 如果 vnpy_tiger 有 requirements.txt, 检查其中列出的其他依赖
   ```
4. 尝试在 Python 解释器中手动导入：
   ```bash
   conda activate simpletrade
   python
   >>> import sys
   >>> import os
   >>> from pathlib import Path
   >>> project_root = Path(__file__).parent.parent.absolute() # In interpreter, adjust path manually if needed
   >>> vendors_path = project_root / "vendors"
   >>> if vendors_path.exists() and str(vendors_path) not in sys.path:
   ...     sys.path.insert(0, str(vendors_path))
   >>> print(sys.path) # Verify vendors path is present
   >>> import vnpy_tiger # See if import works now
   >>> exit()
   ```

## 故障排除

如果遇到 `vnpy_tiger` **运行时**的错误（例如连接失败，而不是导入失败），可以尝试：

1. 检查 `tigeropen` 版本是否与 `vnpy_tiger` 代码兼容。
2. 确认 Tiger API 的配置（ID, Account, Key Path）是否正确。
3. 检查网络连接和 Tiger 服务器状态。
