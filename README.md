# SimpleTrade

一个简单的交易系统，基于修改后的vnpy，不依赖TA-Lib。

## 特点

- 使用pandas-ta替代TA-Lib，无需编译C库
- 修改了vnpy源码，移除了对TA-Lib的依赖
- 提供了简单的API，方便使用

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/simpletrade.git
cd simpletrade

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 使用修改后的vnpy

```python
import sys
from pathlib import Path

# 添加自定义vnpy目录到Python路径
VNPY_CUSTOM_DIR = Path("/path/to/simpletrade/vnpy_custom")
sys.path.insert(0, str(VNPY_CUSTOM_DIR))

# 导入修改后的vnpy模块
from vnpy.trader.utility import ArrayManager

# 创建ArrayManager实例
am = ArrayManager(size=100)

# 使用技术指标
sma = am.sma(10)
ema = am.ema(10)
macd = am.macd(12, 26, 9)
rsi = am.rsi(14)
```

### 使用SimpleTrade API

```python
from simpletrade.api import SimpleTrade

# 创建SimpleTrade实例
st = SimpleTrade()

# 获取数据
data = st.get_data("BTCUSDT", "1d", 100)

# 计算指标
data = st.calculate_indicators(data)

# 回测策略
result = st.backtest(data, strategy="DoubleMa")

# 显示结果
st.show_result(result)
```

## 修改vnpy源码

如果您想自己修改vnpy源码，可以使用以下脚本：

```bash
# 运行修改脚本
python scripts/modify_vnpy.py
```

这个脚本会自动克隆vnpy仓库，修改源码，移除TA-Lib依赖。

## 示例

查看`examples`目录中的示例：

```bash
# 运行示例
python examples/use_custom_vnpy.py
```

## 许可证

MIT
