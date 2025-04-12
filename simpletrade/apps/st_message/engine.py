"""
SimpleTrade消息系统引擎

处理消息指令，并将其分发到相应的处理器。
"""

from typing import Dict, Any, Optional, List, Callable

from simpletrade.core.app import STBaseEngine

class STMessageEngine(STBaseEngine):
    """SimpleTrade消息系统引擎"""

    def __init__(self, main_engine, event_engine, engine_name: str):
        """初始化"""
        super().__init__(main_engine, event_engine, engine_name)
        
        # 命令处理器字典
        self.processors = {}
        
        self.write_log("消息系统引擎初始化成功")
    
    def write_log(self, msg: str):
        """写入日志"""
        self.main_engine.write_log(msg, source=self.engine_name)
    
    def register_processor(self, prefix: str, processor):
        """注册命令处理器"""
        self.processors[prefix] = processor
        self.write_log(f"注册命令处理器: {prefix}")
    
    def process_message(self, message_text: str) -> str:
        """处理消息"""
        # 检查是否是命令
        if not message_text.startswith("/"):
            return None
        
        # 查找匹配的处理器
        for prefix, processor in self.processors.items():
            if message_text.startswith(prefix):
                try:
                    return processor.process(message_text)
                except Exception as e:
                    return f"命令处理错误: {str(e)}"
        
        return "未知命令。使用 `/help` 获取帮助。"
    
    def send_message(self, message: str, target: Optional[str] = None) -> bool:
        """发送消息
        
        参数:
            message (str): 消息内容
            target (str, optional): 目标用户或群组ID
            
        返回:
            bool: 是否发送成功
        """
        # 这里只是一个占位实现，实际应用中需要连接到真实的消息系统
        self.write_log(f"发送消息: {message}" + (f" 到 {target}" if target else ""))
        return True
