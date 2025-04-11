"""
SimpleTrade消息系统测试

提供测试消息指令的功能。
"""

def test_message(engine, message_text: str) -> str:
    """测试消息指令
    
    参数:
        engine: 消息引擎实例
        message_text: 消息文本
        
    返回:
        str: 处理结果
    """
    return engine.process_message(message_text)

def run_interactive_test(engine):
    """运行交互式测试
    
    参数:
        engine: 消息引擎实例
    """
    print("SimpleTrade消息系统测试")
    print("输入消息指令进行测试，输入'exit'退出")
    print("示例: /data query")
    
    while True:
        message = input("> ")
        if message.lower() == "exit":
            break
        
        result = test_message(engine, message)
        print(result or "无响应")
