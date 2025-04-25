"""
数据导入器基类

定义所有数据导入器必须实现的标准接口。
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData

class BaseDataImporter(ABC):
    """数据导入器基类
    
    所有数据导入器必须继承此类并实现 import_data 方法。
    """
    
    def extract_and_validate_params(self, target_config: Dict[str, Any]) -> Dict[str, Any]:
        """从目标配置中提取并验证导入参数
        
        从完整的目标配置中提取此导入器所需的特定参数，并进行验证。
        子类应当重写此方法以实现特定的参数提取和验证逻辑。
        
        Args:
            target_config: 完整的目标配置字典
            
        Returns:
            处理后的参数字典，可直接用于import_data方法
            
        Raises:
            ValueError: 当必要参数缺失或无效时
        """
        # 提取基本参数（所有导入器通用）
        params = {
            "symbol": target_config.get("symbol"),
            "exchange": target_config.get("exchange"),
            "interval": target_config.get("interval"),
            "start_date": target_config.get("start_date"),
            "end_date": target_config.get("end_date")
        }
        
        # 基类默认实现：不提取额外参数
        return params
    
    @abstractmethod
    def import_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **kwargs
    ) -> Tuple[bool, str, List[BarData]]:
        """导入数据的抽象方法
        
        Args:
            symbol: 品种代码
            exchange: 交易所
            interval: K线周期
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 额外参数，可由具体导入器定义
            
        Returns:
            (是否成功, 消息, BarData列表)
        """
        pass 