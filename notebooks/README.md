# Jupyter Notebook 使用指南

## 什么是Jupyter Notebook？

Jupyter Notebook是一个开源的Web应用程序，允许您创建和共享包含实时代码、方程式、可视化和叙述性文本的文档。它是数据科学家、量化分析师和策略开发者的重要工具。

## 在SimpleTrade中的用途

在SimpleTrade系统中，Jupyter Notebook主要用于以下场景：

1. **数据分析**：
   - 加载和探索历史行情数据
   - 计算和可视化技术指标
   - 分析交易品种的统计特性
   - 研究市场模式和相关性

2. **策略开发**：
   - 编写和测试交易策略
   - 可视化策略信号和交易结果
   - 优化策略参数
   - 分析策略性能指标

3. **回测结果分析**：
   - 加载和可视化回测结果
   - 分析策略的盈亏分布
   - 计算风险指标
   - 比较不同策略的性能

4. **实时监控**：
   - 连接到实时交易系统
   - 监控策略运行状态
   - 分析实时交易数据
   - 调整策略参数

## 如何使用

1. **访问Jupyter Notebook**：
   - 启动SimpleTrade系统后，访问 http://localhost:8888
   - 无需密码即可登录（在生产环境中应设置密码）

2. **创建新的Notebook**：
   - 点击右上角的"New"按钮，选择"Python 3"
   - 这将创建一个新的Python Notebook

3. **导入常用库**：
   ```python
   import pandas as pd
   import numpy as np
   import matplotlib.pyplot as plt
   import seaborn as sns
   from datetime import datetime, timedelta
   
   # 设置绘图风格
   plt.style.use('ggplot')
   sns.set_style('whitegrid')
   %matplotlib inline
   
   # 导入vnpy相关模块
   from vnpy.trader.constant import Interval
   from vnpy.trader.database import database_manager
   from vnpy.trader.utility import BarGenerator, ArrayManager
   ```

4. **加载历史数据**：
   ```python
   # 从数据库加载历史数据
   symbol = "BTCUSDT"
   exchange = "BINANCE"
   interval = Interval.MINUTE
   start = datetime(2023, 1, 1)
   end = datetime(2023, 12, 31)
   
   bars = database_manager.load_bar_data(
       symbol=symbol,
       exchange=exchange,
       interval=interval,
       start=start,
       end=end
   )
   
   # 转换为DataFrame
   data = []
   for bar in bars:
       data.append({
           "datetime": bar.datetime,
           "open": bar.open_price,
           "high": bar.high_price,
           "low": bar.low_price,
           "close": bar.close_price,
           "volume": bar.volume
       })
   
   df = pd.DataFrame(data)
   df.set_index("datetime", inplace=True)
   
   # 显示数据
   df.head()
   ```

5. **计算技术指标**：
   ```python
   # 计算移动平均线
   df["ma5"] = df["close"].rolling(5).mean()
   df["ma10"] = df["close"].rolling(10).mean()
   df["ma20"] = df["close"].rolling(20).mean()
   
   # 计算MACD
   def calculate_macd(df, fast=12, slow=26, signal=9):
       df = df.copy()
       df["ema_fast"] = df["close"].ewm(span=fast, adjust=False).mean()
       df["ema_slow"] = df["close"].ewm(span=slow, adjust=False).mean()
       df["macd"] = df["ema_fast"] - df["ema_slow"]
       df["signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
       df["histogram"] = df["macd"] - df["signal"]
       return df
   
   df = calculate_macd(df)
   ```

6. **可视化数据**：
   ```python
   # 绘制K线图和移动平均线
   plt.figure(figsize=(12, 6))
   plt.plot(df.index, df["close"], label="Close")
   plt.plot(df.index, df["ma5"], label="MA5")
   plt.plot(df.index, df["ma10"], label="MA10")
   plt.plot(df.index, df["ma20"], label="MA20")
   plt.title(f"{symbol} Price and Moving Averages")
   plt.xlabel("Date")
   plt.ylabel("Price")
   plt.legend()
   plt.grid(True)
   plt.show()
   
   # 绘制MACD
   plt.figure(figsize=(12, 6))
   plt.subplot(2, 1, 1)
   plt.plot(df.index, df["close"], label="Close")
   plt.title(f"{symbol} Price")
   plt.legend()
   
   plt.subplot(2, 1, 2)
   plt.plot(df.index, df["macd"], label="MACD")
   plt.plot(df.index, df["signal"], label="Signal")
   plt.bar(df.index, df["histogram"], label="Histogram")
   plt.title("MACD")
   plt.legend()
   plt.tight_layout()
   plt.show()
   ```

7. **保存Notebook**：
   - 点击"File" -> "Save"或使用快捷键Ctrl+S
   - Notebook将保存在/app/notebooks目录中

## 示例Notebook

我们提供了一些示例Notebook，帮助您快速上手：

1. **数据分析示例.ipynb**：展示如何加载和分析历史数据
2. **策略开发示例.ipynb**：展示如何开发和测试交易策略
3. **回测分析示例.ipynb**：展示如何分析回测结果
4. **实时监控示例.ipynb**：展示如何监控实时交易数据

## 注意事项

1. Jupyter Notebook服务运行在Docker容器中，数据保存在notebooks数据卷中
2. 重启容器不会丢失Notebook文件，但请定期备份重要的Notebook
3. 在生产环境中，应设置Jupyter Notebook的访问密码
4. 避免在Notebook中运行耗时的计算，这可能会影响其他服务的性能
