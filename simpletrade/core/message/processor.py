"""
SimpleTrade消息处理器

处理消息指令，并将其分发到相应的处理器。
"""

from typing import Dict, Any, Optional, List, Callable


class CommandProcessor:
    """命令处理器基类"""
    
    def __init__(self, prefix: str):
        """初始化
        
        参数:
            prefix: 命令前缀
        """
        self.prefix = prefix
    
    def process(self, command: str) -> str:
        """处理命令
        
        参数:
            command: 命令文本
            
        返回:
            str: 处理结果
        """
        raise NotImplementedError("子类必须实现process方法")


class MessageProcessor:
    """消息处理器"""
    
    def __init__(self):
        """初始化"""
        self.processors: Dict[str, CommandProcessor] = {}
    
    def register_processor(self, processor: CommandProcessor):
        """注册命令处理器
        
        参数:
            processor: 命令处理器
        """
        self.processors[processor.prefix] = processor
    
    def process(self, message: str) -> str:
        """处理消息
        
        参数:
            message: 消息文本
            
        返回:
            str: 处理结果
        """
        # 检查是否是命令
        if not message.startswith("/"):
            return ""
        
        # 查找匹配的处理器
        for prefix, processor in self.processors.items():
            if message.startswith(prefix):
                try:
                    return processor.process(message)
                except Exception as e:
                    return f"命令处理错误: {str(e)}"
        
        return "未知命令。使用 `/help` 获取帮助。"
