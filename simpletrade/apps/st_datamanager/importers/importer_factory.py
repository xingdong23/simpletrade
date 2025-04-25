"""
数据导入器工厂

负责管理和创建不同的数据导入器实例。
"""

from typing import Dict, Type, Optional
import logging

from .base_importer import BaseDataImporter

logger = logging.getLogger(__name__)

class ImporterFactory:
    """数据导入器工厂
    
    负责管理和创建各种数据导入器。
    """
    
    _importers: Dict[str, Type[BaseDataImporter]] = {}
    
    @classmethod
    def register_importer(cls, source_name: str, importer_class: Type[BaseDataImporter]) -> None:
        """注册新的导入器类
        
        Args:
            source_name: 数据源名称
            importer_class: 导入器类，必须继承 BaseDataImporter
        """
        if not issubclass(importer_class, BaseDataImporter):
            raise TypeError(f"Importer class must inherit from BaseDataImporter")
        
        cls._importers[source_name.lower()] = importer_class
        logger.info(f"Registered data importer for source: {source_name}")
    
    @classmethod
    def create_importer(cls, source_name: str) -> Optional[BaseDataImporter]:
        """创建指定数据源的导入器实例
        
        Args:
            source_name: 数据源名称
            
        Returns:
            导入器实例，如果数据源未注册则返回 None
        """
        importer_class = cls._importers.get(source_name.lower())
        if not importer_class:
            logger.warning(f"No registered importer found for source: {source_name}")
            return None
        
        return importer_class()
    
    @classmethod
    def get_supported_sources(cls) -> list:
        """获取所有支持的数据源列表"""
        return list(cls._importers.keys()) 