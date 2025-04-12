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
uvicorn simpletrade.api.server:app --host 0.0.0.0 --port 8000 --reload
```

参数说明：
- `--host 0.0.0.0`：允许从任何 IP 地址访问 API 服务
- `--port 8000`：API 服务监听的端口
- `--reload`：当代码变更时自动重新加载服务（开发模式）

启动成功后，可以通过访问 http://localhost:8000/docs 查看 API 文档。

## 启动前端 Web 界面

在项目根目录下的 `web-frontend` 目录中执行以下命令启动前端 Web 界面：

```bash
cd web-frontend
npm run serve
```

启动成功后，通常可以通过访问 http://localhost:8080 查看前端界面。

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
