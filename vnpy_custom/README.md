# 修改后的vnpy源码

这个目录包含了修改后的vnpy源码，使用pandas-ta替代TA-Lib，不再依赖TA-Lib库。

## 修改内容

1. **使用pandas-ta替代TA-Lib**：
   - 修改了`vnpy/trader/utility.py`文件中的`ArrayManager`类，使用pandas-ta替代TA-Lib
   - 添加了辅助函数`_to_series`，将numpy数组转换为pandas Series

2. **创建必要的模块**：
   - 创建了`vnpy/app/cta_strategy`模块，包括`base.py`、`engine.py`、`backtesting.py`等文件
   - 实现了CTA策略的基本功能

3. **简化依赖**：
   - 移除了对TA-Lib的依赖，使用纯Python实现的pandas-ta库
   - 减少了系统依赖，提高了可移植性

## 使用方法

1. **导入路径设置**：
   ```python
   import sys
   from pathlib import Path

   # 添加vnpy源码目录到Python路径
   VNPY_CUSTOM_DIR = Path(__file__).parent.parent / "vnpy_custom"
   if VNPY_CUSTOM_DIR.exists() and str(VNPY_CUSTOM_DIR) not in sys.path:
       sys.path.insert(0, str(VNPY_CUSTOM_DIR))
   ```

2. **导入vnpy模块**：
   ```python
   from vnpy.trader.utility import ArrayManager
   from vnpy.trader.object import BarData
   from vnpy.trader.constant import Interval, Direction
   from vnpy.app.cta_strategy.template import CtaTemplate
   ```

3. **使用ArrayManager计算技术指标**：
   ```python
   # 创建ArrayManager实例
   am = ArrayManager(size=100)

   # 更新K线数据
   am.update_bar(bar)

   # 计算技术指标
   sma = am.sma(10)
   ema = am.ema(10)
   macd, signal, hist = am.macd(12, 26, 9)
   rsi = am.rsi(14)
   ```

## 依赖

- pandas>=1.3.0
- numpy>=1.20.0
- pandas-ta>=0.3.14b0

## 注意事项

1. **兼容性**：
   - 这个修改后的vnpy源码与原版vnpy的API保持一致，可以无缝替换
   - 但是，由于使用了pandas-ta替代TA-Lib，可能会有一些细微的差异

2. **性能**：
   - pandas-ta是纯Python实现，性能可能不如TA-Lib
   - 但是，对于大多数应用场景，性能差异不会很明显

3. **numpy.NaN兼容性问题**：
   - 在新版本的numpy中，`NaN`已经改为`nan`（小写）
   - 我们在`simpletrade/__init__.py`中添加了修复代码，确保兼容性
   - 如果遇到`ImportError: cannot import name 'NaN' from 'numpy'`错误，请确保在导入pandas-ta之前执行了修复代码

4. **维护**：
   - 这个修改后的vnpy源码是基于vnpy 3.0.0版本的，如果vnpy更新，可能需要重新修改
   - 建议定期检查vnpy的更新，并将修改同步到最新版本
