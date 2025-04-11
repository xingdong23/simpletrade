# SimpleTrade 安装指南

本文档描述了如何安装和设置SimpleTrade项目。

## 环境要求

- Python 3.8+
- Conda 环境管理器

## 安装步骤

### 1. 克隆仓库

```bash
git clone --recursive https://github.com/yourusername/simpletrade.git
cd simpletrade
```

注意`--recursive`参数，这是为了同时克隆vnpy子模块。

### 2. 创建Conda环境

```bash
conda create -n simpletrade python=3.8
conda activate simpletrade
```

### 3. 安装依赖

```bash
# 安装vnpy
cd vnpy
pip install -e .
cd ..

# 安装simpletrade
pip install -e .
```

### 4. 验证安装

```bash
# 运行示例
python examples/data_management_example.py
```

## 常见问题

### 依赖冲突

如果遇到依赖冲突，特别是与NumPy相关的冲突，可以尝试：

```bash
pip install numpy==2.2.0
```

### vnpy导入错误

如果遇到vnpy导入错误，确保已经正确安装了vnpy：

```bash
cd vnpy
pip install -e .
```

## 开发环境设置

对于开发人员，建议使用以下工具：

- VSCode 或 PyCharm 作为IDE
- pytest 进行测试
- black 和 isort 进行代码格式化

安装开发依赖：

```bash
pip install pytest black isort
```
