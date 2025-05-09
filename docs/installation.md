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

### 3. 安装后端依赖

+ **重要**: 本项目采用混合依赖管理：
+ - vnpy 核心及官方插件通过 `pip` 安装。
+ - 自定义的 `vnpy_tiger` 网关位于 `vendors/vnpy_tiger` 目录，需要单独安装其依赖并确保路径可访问 (通过`main.py`中的`sys.path`修改实现)。

在激活的环境中，使用 pip 安装 SimpleTrade 及其核心依赖：

```bash
# 安装 vnpy 核心及常用官方插件
# 选择你需要的插件进行安装
pip install vnpy vnpy_ctp vnpy_ib vnpy_datamanager vnpy_sqlite # 注意：移除了 vnpy_tiger

# 以开发模式安装 SimpleTrade (强烈推荐)
pip install -e .

# 安装 FastAPI 和 Uvicorn (用于 API 服务)
pip install fastapi uvicorn[standard] pydantic[email]

# 安装 vnpy_tiger 的依赖 (主要是 tigeropen)
# 确保 tigeropen 已安装
pip install tigeropen
# 如果 vnpy_tiger 有 requirements.txt, 也可以安装它:
# pip install -r vendors/vnpy_tiger/requirements.txt

# 安装 TA-Lib (技术分析库)
conda install -c conda-forge ta-lib
# 或者使用 pip
# pip install ta-lib

# 安装其他可能需要的依赖 (根据需要)
# pip install pandas numpy scikit-learn ...
```

#### 开发模式安装说明

开发模式安装（`pip install -e .`）有以下优势：

1. **不复制代码**：普通安装会将代码复制到 Python 的 site-packages 目录，而开发模式只在 site-packages 中创建一个指向原始代码位置的链接

2. **实时反映代码变化**：当您修改项目代码时，不需要重新安装包，修改会立即生效

3. **解决导入问题**：将项目添加到 Python 路径中，这样 Python 可以正确找到并导入项目中的模块

即使您直接在源码目录中开发，也强烈建议使用开发模式安装，以避免导入错误如 `ModuleNotFoundError: No module named 'simpletrade.api'`。

### 4. 跨平台环境设置

如果您需要在不同的计算机之间切换开发（例如公司电脑和家里的电脑），可以使用以下方法确保环境一致性：

#### 使用环境配置文件

项目根目录下提供了 `environment.yml` 文件，可以用来创建一致的环境：

```bash
# 使用环境文件创建环境
conda env create -f environment.yml
```

#### 使用安装脚本

项目根目录下提供了 `setup_env.sh` 脚本，可以自动化环境设置过程：

```bash
# 使脚本可执行
chmod +x setup_env.sh

# 运行脚本
./setup_env.sh
```

#### 针对不同平台的注意事项

**Intel Mac**

- TA-Lib 可以直接使用 conda 安装：`conda install -c conda-forge ta-lib`
- 如果遇到 TA-Lib 符号加载错误，尝试卸载并重新安装：
  ```bash
  conda run -n simpletrade pip uninstall -y ta-lib
  conda run -n simpletrade pip install ta-lib
  ```

**M1/M2 Mac (Apple Silicon)**

- TA-Lib 可能需要特殊处理，如果 conda 安装失败，可以尝试从源码编译：
  ```bash
  # 安装编译工具
  brew install gcc

  # 下载和编译 TA-Lib
  wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
  tar -xzf ta-lib-0.4.0-src.tar.gz
  cd ta-lib/
  ./configure --prefix=/usr/local
  make
  sudo make install

  # 安装 Python 包
  pip install ta-lib
  ```

**Windows**

- TA-Lib 在 Windows 上安装可能比较复杂，建议下载预编译的二进制文件：
  1. 从 [TA-Lib页面](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib) 下载适合您 Python 版本的 wheel 文件
  2. 安装下载的 wheel 文件：`pip install TA_Lib-0.4.0-cp312-cp312-win_amd64.whl`

#### 使用 Docker （可选）

如果您经常在不同环境之间切换，可以考虑使用 Docker 容器化开发环境。项目根目录下提供了 Dockerfile，可以用来创建一致的开发环境。

### 4. 安装前端依赖

前端使用Vue 2.x和Element UI框架，需要安装Node.js和npm。

```bash
# 进入前端目录
cd web-frontend

# 安装依赖
npm install

# 如果遇到依赖冲突，可以使用以下命令
npm install --legacy-peer-deps
```

### 5. 验证安装

```bash
# 尝试导入 vnpy
python -c "import vnpy; print(vnpy.__version__)"

# 运行后端服务 (参见 docs/startup_guide.md)
# uvicorn simpletrade.api.server:app --reload

# 运行前端服务
# cd web-frontend && npm run serve
```

## 常见问题

### 依赖冲突

如果遇到依赖冲突，尝试创建一个干净的环境并重新安装。检查特定库的版本兼容性。

### vnpy导入错误

如果遇到vnpy导入错误，请确保在**激活的 simpletrade 环境**中运行，并且已使用 `pip install vnpy [插件...]` 安装了 vnpy 及其所需**官方**插件。

+ 对于 `vnpy_tiger` 导入错误，请检查：
+ 1. `vendors/vnpy_tiger` 目录是否存在且包含正确的源代码。
+ 2. `main.py` 文件开头的 `sys.path` 修改是否正确执行。
+ 3. `vnpy_tiger` 的依赖 (`tigeropen` 等) 是否已通过 `pip` 安装。

## 开发环境设置

对于开发人员，建议使用以下工具：

- VSCode 或 PyCharm 作为IDE
- pytest 进行测试
- black 和 isort 进行代码格式化

安装开发依赖：

```bash
pip install pytest black isort
```
