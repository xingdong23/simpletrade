"""
数据导入器包

包含各种数据源导入器的实现。
"""

from .base_importer import BaseDataImporter
from .importer_factory import ImporterFactory
from .qlib_importer import QlibDataImporter

# 注册内置的导入器
ImporterFactory.register_importer("qlib", QlibDataImporter)

__all__ = [
    "BaseDataImporter",
    "ImporterFactory",
    "QlibDataImporter",
]
