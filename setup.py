"""
SimpleTrade安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="simpletrade",
    version="0.1.0",
    description="简单易用的个人量化交易平台",
    author="SimpleTrade Team",
    packages=find_packages(),
    install_requires=[
        # 基础依赖
        "numpy",
        "pandas",
        "matplotlib",
        # API服务依赖
        "fastapi",
        "uvicorn",
        # 数据库依赖
        "sqlalchemy",
        # 其他依赖
        "pyqt5",
    ],
    python_requires=">=3.7",
)
