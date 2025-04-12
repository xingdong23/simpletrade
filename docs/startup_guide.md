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

要验证 `vnpy_tiger` 是否成功加载，可以查看后端 API 服务的启动日志。如果成功加载，日志中应该包含以下信息：

```
vnpy_tiger imported successfully.
Global: Tiger Gateway registered.
```

如果未看到上述信息，可能需要检查 `vnpy_tiger` 的安装状态：

1. 确认 `vnpy_tiger` 已安装：
   ```bash
   conda activate simpletrade
   pip list | grep tiger
   ```

2. 确认可以成功导入：
   ```bash
   conda activate simpletrade
   python -c "import vnpy_tiger; print('vnpy_tiger successfully imported')"
   ```

3. 如果导入失败，尝试重新安装：
   ```bash
   cd vnpy_tiger
   pip install -e .
   ```

## 故障排除

如果遇到 `vnpy_tiger` 加载失败的问题，可以尝试以下步骤：

1. 确认 `tigeropen` 依赖已安装：
   ```bash
   pip install tigeropen
   ```

2. 重新启动应用并检查日志。

3. 如果问题仍然存在，可能需要检查 Python 路径和环境变量。
