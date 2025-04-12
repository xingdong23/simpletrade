# VeighNa Tiger Gateway

老虎证券交易接口，用于对接老虎证券的行情和交易服务。

## 安装

安装环境推荐基于3.0.0版本以上的【[**VeighNa Studio**](https://www.vnpy.com)】。

直接使用pip命令：

```
pip install vnpy_tiger
```

或者下载源代码后，解压后在cmd中运行：

```
pip install .
```

## 使用

以脚本方式启动（script/run.py）：

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

from vnpy_tiger import TigerGateway


def main():
    """主入口函数"""
    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(TigerGateway)
    
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()
```

## 配置

连接老虎证券接口时，需要填写以下字段：

- tiger_id：老虎证券开放平台ID
- account：交易账号
- private_key：私钥文件路径
- server：服务器类型（标准、环球、模拟）
- language：语言（中文、英文）
