# 技术指标参考指南

**最后更新**: 2023-10-15

## 1. 趋势指标

### 1.1 移动平均线 (Moving Average, MA)

**描述**: 计算特定周期内价格的平均值，用于识别价格趋势方向和潜在的支撑/阻力位。

**类型**:
- 简单移动平均线 (SMA)
- 指数移动平均线 (EMA)
- 加权移动平均线 (WMA)
- 平滑移动平均线 (SMMA)

**计算方法**:
```python
# 简单移动平均线 (SMA)
def sma(close_prices, period):
    """
    计算简单移动平均线
    
    参数:
        close_prices (list): 收盘价列表
        period (int): 周期
        
    返回:
        list: SMA值列表
    """
    if len(close_prices) < period:
        return [None] * len(close_prices)
        
    result = [None] * (period - 1)
    for i in range(period - 1, len(close_prices)):
        result.append(sum(close_prices[i - period + 1:i + 1]) / period)
    
    return result

# 指数移动平均线 (EMA)
def ema(close_prices, period):
    """
    计算指数移动平均线
    
    参数:
        close_prices (list): 收盘价列表
        period (int): 周期
        
    返回:
        list: EMA值列表
    """
    if len(close_prices) < period:
        return [None] * len(close_prices)
        
    k = 2 / (period + 1)
    result = [None] * (period - 1)
    result.append(sum(close_prices[:period]) / period)  # 第一个值使用SMA
    
    for i in range(period, len(close_prices)):
        result.append(close_prices[i] * k + result[-1] * (1 - k))
    
    return result
```

**使用场景**:
- 识别价格趋势方向
- 确定潜在的支撑和阻力位
- 作为其他指标的基础
- 交叉信号作为交易触发条件

**在SimpleTrade中的实现**:
- 支持多种移动平均线类型
- 允许自定义参数
- 提供可视化展示
- 支持MA交叉策略

### 1.2 MACD (Moving Average Convergence Divergence)

**描述**: 通过计算两条不同周期移动平均线之间的差值及其平均线，用于识别动量、趋势方向和潜在的反转点。

**组成部分**:
- MACD线: 短期EMA - 长期EMA
- 信号线: MACD线的EMA
- 柱状图: MACD线 - 信号线

**计算方法**:
```python
def macd(close_prices, fast_period=12, slow_period=26, signal_period=9):
    """
    计算MACD指标
    
    参数:
        close_prices (list): 收盘价列表
        fast_period (int): 快线周期，默认12
        slow_period (int): 慢线周期，默认26
        signal_period (int): 信号线周期，默认9
        
    返回:
        tuple: (MACD线, 信号线, 柱状图)
    """
    # 计算快线和慢线EMA
    fast_ema = ema(close_prices, fast_period)
    slow_ema = ema(close_prices, slow_period)
    
    # 计算MACD线
    macd_line = [fast - slow for fast, slow in zip(fast_ema, slow_ema)]
    
    # 计算信号线
    signal_line = ema(macd_line, signal_period)
    
    # 计算柱状图
    histogram = [macd - signal for macd, signal in zip(macd_line, signal_line)]
    
    return macd_line, signal_line, histogram
```

**使用场景**:
- 识别趋势方向和强度
- 发现潜在的买入和卖出信号
- 识别背离(价格创新高/新低但MACD未能确认)
- 确认其他指标的信号

**在SimpleTrade中的实现**:
- 支持自定义参数
- 提供可视化展示
- 支持背离检测
- 集成到策略引擎

### 1.3 布林带 (Bollinger Bands)

**描述**: 由中轨(SMA)和上下轨(中轨加减标准差的倍数)组成，用于衡量价格波动性和潜在的超买/超卖区域。

**组成部分**:
- 中轨: N周期SMA
- 上轨: 中轨 + K倍标准差
- 下轨: 中轨 - K倍标准差

**计算方法**:
```python
import numpy as np

def bollinger_bands(close_prices, period=20, std_dev=2):
    """
    计算布林带
    
    参数:
        close_prices (list): 收盘价列表
        period (int): 周期，默认20
        std_dev (float): 标准差倍数，默认2
        
    返回:
        tuple: (上轨, 中轨, 下轨)
    """
    # 计算中轨(SMA)
    middle = sma(close_prices, period)
    
    # 计算标准差
    std = [None] * (period - 1)
    for i in range(period - 1, len(close_prices)):
        values = close_prices[i - period + 1:i + 1]
        std.append(np.std(values, ddof=1))
    
    # 计算上下轨
    upper = [mid + std_dev * s if mid is not None else None for mid, s in zip(middle, std)]
    lower = [mid - std_dev * s if mid is not None else None for mid, s in zip(middle, std)]
    
    return upper, middle, lower
```

**使用场景**:
- 识别价格波动性
- 确定潜在的超买/超卖区域
- 识别价格通道和突破
- 作为均值回归策略的基础

**在SimpleTrade中的实现**:
- 支持自定义参数
- 提供可视化展示
- 支持带宽和%B指标
- 集成到策略引擎

## 2. 动量指标

### 2.1 相对强弱指数 (Relative Strength Index, RSI)

**描述**: 衡量价格变动的强度，用于识别潜在的超买/超卖条件和价格背离。

**计算方法**:
```python
def rsi(close_prices, period=14):
    """
    计算RSI指标
    
    参数:
        close_prices (list): 收盘价列表
        period (int): 周期，默认14
        
    返回:
        list: RSI值列表
    """
    if len(close_prices) <= period:
        return [None] * len(close_prices)
    
    # 计算价格变化
    changes = [close_prices[i] - close_prices[i-1] for i in range(1, len(close_prices))]
    
    # 初始化结果列表
    result = [None] * (period)
    
    # 计算第一个RSI值
    gains = sum(max(change, 0) for change in changes[:period])
    losses = sum(abs(min(change, 0)) for change in changes[:period])
    
    if losses == 0:
        result.append(100)
    else:
        rs = gains / losses
        result.append(100 - (100 / (1 + rs)))
    
    # 使用平滑方法计算后续RSI值
    for i in range(period + 1, len(close_prices)):
        change = close_prices[i-1] - close_prices[i-2]
        gain = max(change, 0)
        loss = abs(min(change, 0))
        
        gains = (gains * (period - 1) + gain) / period
        losses = (losses * (period - 1) + loss) / period
        
        if losses == 0:
            result.append(100)
        else:
            rs = gains / losses
            result.append(100 - (100 / (1 + rs)))
    
    return result
```

**使用场景**:
- 识别超买/超卖条件(通常>70为超买，<30为超卖)
- 发现价格背离(价格创新高/新低但RSI未能确认)
- 识别趋势强度
- 作为交易信号的过滤器

**在SimpleTrade中的实现**:
- 支持自定义参数
- 提供可视化展示
- 支持背离检测
- 集成到策略引擎

### 2.2 随机指标 (Stochastic Oscillator)

**描述**: 比较收盘价在最高价和最低价范围内的位置，用于识别潜在的超买/超卖条件和价格动量。

**组成部分**:
- %K线: 快速随机线
- %D线: %K的移动平均

**计算方法**:
```python
def stochastic(high_prices, low_prices, close_prices, k_period=14, d_period=3):
    """
    计算随机指标
    
    参数:
        high_prices (list): 最高价列表
        low_prices (list): 最低价列表
        close_prices (list): 收盘价列表
        k_period (int): %K周期，默认14
        d_period (int): %D周期，默认3
        
    返回:
        tuple: (%K, %D)
    """
    if len(close_prices) < k_period:
        return [None] * len(close_prices), [None] * len(close_prices)
    
    # 计算%K
    k_values = [None] * (k_period - 1)
    for i in range(k_period - 1, len(close_prices)):
        highest_high = max(high_prices[i - k_period + 1:i + 1])
        lowest_low = min(low_prices[i - k_period + 1:i + 1])
        
        if highest_high == lowest_low:
            k_values.append(50)  # 避免除以零
        else:
            k_values.append(100 * (close_prices[i] - lowest_low) / (highest_high - lowest_low))
    
    # 计算%D (简单移动平均)
    d_values = sma(k_values, d_period)
    
    return k_values, d_values
```

**使用场景**:
- 识别超买/超卖条件(通常>80为超买，<20为超卖)
- 发现%K和%D的交叉信号
- 识别价格背离
- 确认其他指标的信号

**在SimpleTrade中的实现**:
- 支持自定义参数
- 提供可视化展示
- 支持背离检测
- 集成到策略引擎

## 3. 成交量指标

### 3.1 成交量加权平均价格 (Volume Weighted Average Price, VWAP)

**描述**: 根据成交量加权计算的平均价格，用于评估当前价格相对于日内交易的价值。

**计算方法**:
```python
def vwap(high_prices, low_prices, close_prices, volumes):
    """
    计算成交量加权平均价格
    
    参数:
        high_prices (list): 最高价列表
        low_prices (list): 最低价列表
        close_prices (list): 收盘价列表
        volumes (list): 成交量列表
        
    返回:
        list: VWAP值列表
    """
    typical_prices = [(h + l + c) / 3 for h, l, c in zip(high_prices, low_prices, close_prices)]
    
    cumulative_tp_vol = 0
    cumulative_vol = 0
    result = []
    
    for tp, vol in zip(typical_prices, volumes):
        cumulative_tp_vol += tp * vol
        cumulative_vol += vol
        
        if cumulative_vol == 0:
            result.append(None)
        else:
            result.append(cumulative_tp_vol / cumulative_vol)
    
    return result
```

**使用场景**:
- 评估当前价格是否合理
- 作为日内交易的参考价格
- 识别潜在的支撑和阻力位
- 作为算法交易的基准价格

**在SimpleTrade中的实现**:
- 支持日内和跨日VWAP计算
- 提供可视化展示
- 支持VWAP偏差分析
- 集成到策略引擎

### 3.2 能量潮指标 (On-Balance Volume, OBV)

**描述**: 将成交量累加或减去，取决于收盘价相对于前一收盘价的变化，用于确认价格趋势。

**计算方法**:
```python
def obv(close_prices, volumes):
    """
    计算能量潮指标
    
    参数:
        close_prices (list): 收盘价列表
        volumes (list): 成交量列表
        
    返回:
        list: OBV值列表
    """
    if len(close_prices) == 0:
        return []
    
    result = [0]  # 初始值设为0
    
    for i in range(1, len(close_prices)):
        if close_prices[i] > close_prices[i-1]:
            result.append(result[-1] + volumes[i])
        elif close_prices[i] < close_prices[i-1]:
            result.append(result[-1] - volumes[i])
        else:
            result.append(result[-1])
    
    return result
```

**使用场景**:
- 确认价格趋势
- 识别价格和成交量背离
- 预测潜在的价格突破
- 作为交易信号的过滤器

**在SimpleTrade中的实现**:
- 提供可视化展示
- 支持背离检测
- 支持OBV移动平均线
- 集成到策略引擎

## 4. 波动性指标

### 4.1 平均真实波幅 (Average True Range, ATR)

**描述**: 衡量市场波动性的指标，不考虑价格方向，只关注价格波动的幅度。

**计算方法**:
```python
def atr(high_prices, low_prices, close_prices, period=14):
    """
    计算平均真实波幅
    
    参数:
        high_prices (list): 最高价列表
        low_prices (list): 最低价列表
        close_prices (list): 收盘价列表
        period (int): 周期，默认14
        
    返回:
        list: ATR值列表
    """
    if len(close_prices) < 2:
        return [None] * len(close_prices)
    
    # 计算真实波幅(TR)
    tr_values = [high_prices[0] - low_prices[0]]  # 第一个TR值
    
    for i in range(1, len(close_prices)):
        tr = max(
            high_prices[i] - low_prices[i],  # 当日价格范围
            abs(high_prices[i] - close_prices[i-1]),  # 当日最高与前收盘价差
            abs(low_prices[i] - close_prices[i-1])  # 当日最低与前收盘价差
        )
        tr_values.append(tr)
    
    # 计算ATR (使用Wilder的平滑方法)
    atr_values = [None] * (period - 1)
    atr_values.append(sum(tr_values[:period]) / period)  # 第一个ATR值
    
    for i in range(period, len(tr_values)):
        atr_values.append((atr_values[-1] * (period - 1) + tr_values[i]) / period)
    
    return atr_values
```

**使用场景**:
- 设置止损位置
- 确定价格目标
- 评估市场波动性
- 作为头寸规模的参考

**在SimpleTrade中的实现**:
- 支持自定义参数
- 提供可视化展示
- 支持基于ATR的止损策略
- 集成到风险管理模块

### 4.2 波动率指标 (Volatility Index, VIX)

**描述**: 基于期权价格计算的市场预期波动率，常被称为"恐慌指数"。

**使用场景**:
- 评估市场情绪
- 预测潜在的市场转折点
- 作为交易信号的过滤器
- 风险管理

**在SimpleTrade中的实现**:
- 提供VIX数据获取
- 支持VIX与价格的相关性分析
- 集成到市场情绪分析模块

## 5. 自定义指标

### 5.1 多指标组合

在SimpleTrade中，我们将支持多指标组合，允许用户创建自定义的复合指标：

```python
def custom_indicator(close_prices, high_prices, low_prices, volumes, **params):
    """
    自定义指标示例：RSI和MACD的组合
    
    参数:
        close_prices (list): 收盘价列表
        high_prices (list): 最高价列表
        low_prices (list): 最低价列表
        volumes (list): 成交量列表
        params (dict): 自定义参数
        
    返回:
        dict: 组合指标结果
    """
    # 计算RSI
    rsi_values = rsi(close_prices, params.get('rsi_period', 14))
    
    # 计算MACD
    macd_line, signal_line, histogram = macd(
        close_prices, 
        params.get('fast_period', 12),
        params.get('slow_period', 26),
        params.get('signal_period', 9)
    )
    
    # 组合指标逻辑
    result = []
    for i in range(len(close_prices)):
        if i < max(params.get('rsi_period', 14), params.get('slow_period', 26) + params.get('signal_period', 9) - 1):
            result.append(None)
            continue
            
        rsi_value = rsi_values[i]
        macd_value = macd_line[i]
        signal_value = signal_line[i]
        
        # 示例逻辑：RSI超卖且MACD金叉
        if rsi_value < params.get('rsi_oversold', 30) and macd_value > signal_value and macd_value < 0:
            result.append(1)  # 买入信号
        # 示例逻辑：RSI超买且MACD死叉
        elif rsi_value > params.get('rsi_overbought', 70) and macd_value < signal_value and macd_value > 0:
            result.append(-1)  # 卖出信号
        else:
            result.append(0)  # 无信号
    
    return {
        'signal': result,
        'rsi': rsi_values,
        'macd': macd_line,
        'signal_line': signal_line,
        'histogram': histogram
    }
```

### 5.2 机器学习增强指标

在SimpleTrade中，我们将支持使用机器学习增强传统技术指标：

```python
def ml_enhanced_indicator(features, close_prices, model=None, **params):
    """
    机器学习增强指标示例
    
    参数:
        features (dict): 特征字典，包含各种技术指标
        close_prices (list): 收盘价列表
        model: 预训练的机器学习模型
        params (dict): 自定义参数
        
    返回:
        dict: 预测结果
    """
    # 准备特征数据
    X = []
    for i in range(len(close_prices)):
        if any(features[key][i] is None for key in features):
            continue
            
        feature_vector = [features[key][i] for key in sorted(features.keys())]
        X.append(feature_vector)
    
    # 使用模型预测
    if model is None:
        # 如果没有提供模型，返回None
        return {'prediction': [None] * len(close_prices)}
    
    predictions = model.predict(X)
    
    # 将预测结果映射回原始时间序列
    result = [None] * len(close_prices)
    j = 0
    for i in range(len(close_prices)):
        if any(features[key][i] is None for key in features):
            continue
            
        result[i] = predictions[j]
        j += 1
    
    return {'prediction': result}
```

## 6. 指标使用最佳实践

### 6.1 参数优化

在SimpleTrade中，我们将提供指标参数优化工具：

```python
def optimize_indicator_params(indicator_func, data, target_func, param_grid, **kwargs):
    """
    优化指标参数
    
    参数:
        indicator_func: 指标计算函数
        data: 价格数据
        target_func: 目标函数，用于评估指标性能
        param_grid: 参数网格，包含要测试的参数组合
        kwargs: 其他参数
        
    返回:
        dict: 最优参数组合和性能指标
    """
    best_score = float('-inf')
    best_params = None
    
    # 遍历参数组合
    for params in param_grid:
        # 计算指标
        indicator_values = indicator_func(data, **params)
        
        # 评估性能
        score = target_func(indicator_values, data, **kwargs)
        
        # 更新最优参数
        if score > best_score:
            best_score = score
            best_params = params
    
    return {
        'best_params': best_params,
        'best_score': best_score
    }
```

### 6.2 指标组合策略

在SimpleTrade中，我们将支持多指标组合策略：

```python
def multi_indicator_strategy(data, indicators, rules, **kwargs):
    """
    多指标组合策略
    
    参数:
        data: 价格数据
        indicators: 指标字典，包含各种技术指标
        rules: 交易规则列表
        kwargs: 其他参数
        
    返回:
        dict: 策略信号和性能指标
    """
    signals = [0] * len(data['close'])
    
    # 应用交易规则
    for i in range(len(data['close'])):
        # 跳过没有足够数据的时间点
        if any(indicators[key][i] is None for key in indicators):
            continue
        
        # 评估所有规则
        rule_results = []
        for rule in rules:
            result = rule(indicators, i, **kwargs)
            rule_results.append(result)
        
        # 根据规则结果生成信号
        if all(result > 0 for result in rule_results):
            signals[i] = 1  # 买入信号
        elif all(result < 0 for result in rule_results):
            signals[i] = -1  # 卖出信号
    
    return {'signals': signals}
```

### 6.3 指标可视化

在SimpleTrade中，我们将提供丰富的指标可视化工具，帮助用户理解指标行为和交易信号：

```python
def visualize_indicators(data, indicators, signals=None, **kwargs):
    """
    可视化技术指标和交易信号
    
    参数:
        data: 价格数据
        indicators: 指标字典，包含各种技术指标
        signals: 交易信号列表
        kwargs: 其他参数
        
    返回:
        图表对象
    """
    # 实现可视化逻辑
    # ...
    
    return chart
```

通过这些工具和最佳实践，SimpleTrade将帮助用户更有效地使用技术指标，提高交易决策的质量和效率。
