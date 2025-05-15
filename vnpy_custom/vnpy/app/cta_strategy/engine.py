"""
CTA策略引擎
"""

from vnpy.trader.engine import BaseEngine

class CtaEngine(BaseEngine):
    """CTA策略引擎"""
    
    def __init__(self, main_engine, event_engine):
        """构造函数"""
        super().__init__(main_engine, event_engine, "CtaStrategy")
        
        self.strategies = {}
        
    def init_engine(self):
        """初始化引擎"""
        pass
        
    def close(self):
        """关闭引擎"""
        pass
