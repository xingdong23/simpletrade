# SimpleTrade 安装指南

本文档描述了如何安装和设置SimpleTrade项目。

## 环境要求

- Python 3.10+ (推荐)
- Conda 环境管理器 (推荐) 或其他 Python 环境管理工具

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/simpletrade.git
cd simpletrade
```

### 2. 创建并激活 Python 环境

**使用 Conda (推荐):**
```bash
conda create -n simpletrade python=3.10
conda activate simpletrade
```

**或使用 venv:**
```bash
python -m venv simpletrade_env
source simpletrade_env/bin/activate  # Linux/macOS
# simpletrade_env\Scripts\activate   # Windows
```

### 3. 安装依赖

在激活的环境中，使用 pip 安装 SimpleTrade 及其核心依赖：

```bash
# 安装 vnpy 核心及常用插件
# 选择你需要的插件进行安装
pip install vnpy vnpy_ctp vnpy_ib vnpy_tiger vnpy_datamanager vnpy_sqlite

# 安装 SimpleTrade (通常在开发模式下使用)
# pip install -e .

# 安装 FastAPI 和 Uvicorn (用于 API 服务)
pip install fastapi uvicorn[standard] pydantic[email]

# 安装其他可能需要的依赖 (根据需要)
# 例如 TA-Lib:
# conda install -c conda-forge ta-lib
# 或其他库:
# pip install pandas numpy scikit-learn ...
```

### 4. 验证安装

```bash
# 尝试导入 vnpy
python -c "import vnpy; print(vnpy.__version__)"

# 运行后端服务 (参见 docs/startup_guide.md)
# uvicorn simpletrade.api.server:app --reload
```

## 常见问题

### 依赖冲突

如果遇到依赖冲突，尝试创建一个干净的环境并重新安装。检查特定库的版本兼容性。

### vnpy导入错误

如果遇到vnpy导入错误，请确保在**激活的 simpletrade 环境**中运行，并且已使用 `pip install vnpy [插件...]` 安装了 vnpy 及其所需插件。

## 开发环境设置

对于开发人员，建议使用以下工具：

- VSCode 或 PyCharm 作为IDE
- pytest 进行测试
- black 和 isort 进行代码格式化

安装开发依赖：

```bash
pip install pytest black isort
```
