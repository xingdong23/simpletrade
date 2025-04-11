# SimpleTrade AI模型训练与部署指南

**版本**: 0.1
**日期**: 2023-10-15
**状态**: 初稿

## 1. 文档目的

本文档详细描述 SimpleTrade 交易平台中AI模型的训练流程、数据处理和模型部署方法，为开发团队提供明确的AI功能实现指导。

## 2. AI功能概述

SimpleTrade 平台集成了多种AI功能，主要包括：

1. **市场分析**: 基于技术指标和历史数据分析市场状况
2. **价格预测**: 预测股票/期货价格的未来走势
3. **交易信号生成**: 生成买入/卖出信号
4. **风险评估**: 评估交易风险和波动性
5. **情绪分析**: 分析市场情绪和新闻影响

这些功能依赖于不同类型的机器学习模型，需要大量历史数据进行训练和验证。

## 3. 数据获取与处理

### 3.1 数据源

SimpleTrade 使用以下数据源获取训练数据：

1. **交易所API**: 获取官方行情数据
2. **数据供应商**: 如Wind、同花顺等
3. **公开数据集**: 如Yahoo Finance、Quandl等
4. **新闻和社交媒体**: 用于情绪分析

### 3.2 数据获取流程

```
1. 数据源配置 --> 2. 定时任务设置 --> 3. 数据下载
       |                                |
       v                                v
6. 数据验证 <-- 5. 数据清洗 <-- 4. 原始数据存储
       |
       v
7. 处理后数据存储
```

### 3.3 数据预处理

#### 3.3.1 数据清洗

1. **缺失值处理**:
   - 检测缺失值
   - 根据数据特性选择填充方法（前值填充、插值等）
   - 对于缺失过多的数据可能需要丢弃

2. **异常值处理**:
   - 使用统计方法检测异常值（如Z-score、IQR）
   - 对异常值进行修正或标记

3. **重复数据处理**:
   - 检测并删除重复记录
   - 处理时间重叠的数据

#### 3.3.2 特征工程

1. **技术指标计算**:
   - 移动平均线（MA）
   - 相对强弱指标（RSI）
   - MACD指标
   - 布林带
   - 成交量指标

2. **时间特征提取**:
   - 交易日特征
   - 季节性特征
   - 周期性特征

3. **价格特征**:
   - 价格变化率
   - 价格波动性
   - 价格区间特征

4. **基本面特征**:
   - 财务指标
   - 行业指标
   - 宏观经济指标

### 3.4 数据存储

1. **原始数据存储**:
   - 使用MongoDB存储原始行情数据
   - 按品种和时间周期组织数据
   - 实现数据版本控制

2. **处理后数据存储**:
   - 使用结构化格式存储处理后的特征数据
   - 支持快速查询和检索
   - 实现特征数据缓存机制

## 4. 模型设计与训练

### 4.1 模型类型

SimpleTrade 使用以下类型的模型：

1. **回归模型**:
   - 线性回归
   - 支持向量回归（SVR）
   - 随机森林回归
   - 梯度提升树（XGBoost、LightGBM）

2. **分类模型**:
   - 逻辑回归
   - 支持向量机（SVM）
   - 随机森林分类
   - 梯度提升树分类

3. **时间序列模型**:
   - ARIMA
   - Prophet
   - 指数平滑

4. **深度学习模型**:
   - 长短期记忆网络（LSTM）
   - 门控循环单元（GRU）
   - 卷积神经网络（CNN）
   - Transformer模型

5. **集成模型**:
   - 投票集成
   - 堆叠集成
   - 加权集成

### 4.2 模型训练流程

```
1. 数据准备 --> 2. 特征选择 --> 3. 数据划分
       |                                |
       v                                v
6. 模型评估 <-- 5. 模型训练 <-- 4. 参数调优
       |                                ^
       v                                |
7. 模型保存 ---------------->
```

#### 4.2.1 数据划分

对于监督学习模型，数据划分遵循以下原则：

1. **时间划分**:
   - 训练集: 70-80%的历史数据
   - 验证集: 10-15%的历史数据
   - 测试集: 10-15%的最新数据

2. **时间顺序**:
   - 保持时间顺序，不随机划分
   - 训练集必须在验证集和测试集之前

3. **滚动窗口**:
   - 使用滚动窗口方法进行训练和验证
   - 定期重新训练模型

#### 4.2.2 参数调优

1. **网格搜索**:
   - 定义参数搜索空间
   - 使用交叉验证评估每组参数
   - 选择最佳参数组合

2. **贝叶斯优化**:
   - 使用贝叶斯优化进行自动参数调优
   - 定义目标函数和先验分布

3. **逐步调优**:
   - 先调整主要参数
   - 再细调次要参数
   - 最后进行微调

#### 4.2.3 模型训练

1. **单模型训练**:
   - 使用调优后的参数训练模型
   - 监控训练过程中的损失函数变化
   - 实现早停机制防止过拟合

2. **集成模型训练**:
   - 训练多个基础模型
   - 使用验证集训练集成器
   - 实现交叉验证的堆叠集成

### 4.3 模型评估

#### 4.3.1 评估指标

1. **回归模型指标**:
   - 均方误差 (MSE)
   - 平均绝对误差 (MAE)
   - 平均绝对百分比误差 (MAPE)
   - R平方值 (R²)

2. **分类模型指标**:
   - 准确率 (Accuracy)
   - 精确率 (Precision)
   - 召回率 (Recall)
   - F1分数
   - ROC曲线下面积 (AUC)

3. **交易策略指标**:
   - 胜率
   - 盈亏比
   - 复合年化收益率 (CAGR)
   - 最大回撤率 (MDD)
   - 复合年化收益率/最大回撤率 (CAGR/MDD)
   - 复合年化收益率/波动率 (CAGR/波动率)

#### 4.3.2 评估方法

1. **交叉验证**:
   - 时间序列交叉验证
   - 滚动预测验证
   - 嵌套交叉验证

2. **回测测试**:
   - 历史数据回测
   - 事件验证
   - 压力测试

3. **模拟交易**:
   - 在测试集上进行模拟交易
   - 考虑交易成本和滑点
   - 评估实际交易效果

#### 4.3.3 模型解释

1. **特征重要性**:
   - 随机森林特征重要性
   - 树模型特征重要性
   - 排列置换特征重要性

2. **模型解释技术**:
   - SHAP值
   - LIME解释
   - 部分依赖图

3. **可视化解释**:
   - 决策树可视化
   - 特征重要性图
   - SHAP依赖图

## 5. 模型部署

### 5.1 模型存储

1. **模型序列化**:
   - 使用Pickle/Joblib序列化模型
   - 保存模型参数和超参数
   - 实现模型版本控制

2. **模型存储结构**:
   ```
   models/
   ├── price_prediction/
   │   ├── v1.0.0/
   │   │   ├── model.pkl
   │   │   ├── metadata.json
   │   │   └── preprocessing.pkl
   │   └── v1.1.0/
   │       ├── model.pkl
   │       ├── metadata.json
   │       └── preprocessing.pkl
   ├── signal_generation/
   │   ├── v1.0.0/
   │   └── ...
   └── risk_assessment/
       ├── v1.0.0/
       └── ...
   ```

3. **元数据管理**:
   - 记录模型训练参数
   - 记录训练数据信息
   - 记录模型性能指标

### 5.2 模型服务化

1. **REST API**:
   - 使用FastAPI开发模型服务API
   - 实现模型预测端点
   - 支持批量预测和单条预测

2. **异步任务**:
   - 实现异步预测任务
   - 使用消息队列处理预测请求
   - 支持长时间运行的分析任务

3. **模型缓存**:
   - 实现预测结果缓存
   - 使用Redis缓存频繁请求
   - 实现缓存失效策略

### 5.3 模型集成

1. **与vnpy集成**:
   - 在st_ml插件中集成模型
   - 实现模型加载和预测接口
   - 与交易策略集成

2. **与微信小程序集成**:
   - 实现分析结果展示
   - 支持交互式分析请求
   - 实现分析报告分享

3. **与消息系统集成**:
   - 支持通过消息指令请求分析
   - 实现分析结果推送
   - 支持定时分析报告

### 5.4 模型监控与更新

1. **模型监控**:
   - 监控模型预测性能
   - 检测模型漏洞
   - 记录模型使用统计

2. **模型更新**:
   - 定期重新训练模型
   - 实现模型热更新
   - 维护模型版本历史

3. **A/B测试**:
   - 实现模型版本A/B测试
   - 比较不同模型的性能
   - 基于测试结果自动选择最佳模型

## 6. 实现示例

### 6.1 价格预测模型

```python
# 价格预测模型示例

# 导入库
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib

# 特征工程函数
def calculate_features(df):
    """Calculate technical indicators as features"""
    # 添加移动平均线
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()

    # 添加相对强弱指标
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # 添加MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    # 添加波动率
    df['volatility'] = df['close'].rolling(window=20).std()

    # 添加价格变化
    df['price_change'] = df['close'].pct_change()
    df['price_change_5'] = df['close'].pct_change(periods=5)

    # 删除NaN值
    df.dropna(inplace=True)

    return df

# 模型训练函数
def train_price_prediction_model(df, target_column='close', prediction_horizon=5):
    """Train a price prediction model"""
    # 准备特征和目标
    features = df.drop(['open', 'high', 'low', 'close', 'volume', 'datetime'], axis=1)
    target = df[target_column].shift(-prediction_horizon)  # 预测未来N天的价格

    # 删除目标中的NaN值
    features = features[~target.isna()]
    target = target[~target.isna()]

    # 时间序列划分
    tscv = TimeSeriesSplit(n_splits=5)

    # 创建模型管道
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    # 交叉验证
    cv_scores = []
    for train_idx, test_idx in tscv.split(features):
        X_train, X_test = features.iloc[train_idx], features.iloc[test_idx]
        y_train, y_test = target.iloc[train_idx], target.iloc[test_idx]

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        cv_scores.append({'mse': mse, 'mae': mae})

    # 在全部数据上训练最终模型
    model.fit(features, target)

    # 计算特征重要性
    feature_importance = model.named_steps['regressor'].feature_importances_
    feature_names = features.columns
    importance_df = pd.DataFrame({'feature': feature_names, 'importance': feature_importance})
    importance_df = importance_df.sort_values('importance', ascending=False)

    # 保存模型和元数据
    model_info = {
        'model': model,
        'feature_importance': importance_df.to_dict(),
        'cv_scores': cv_scores,
        'prediction_horizon': prediction_horizon,
        'target_column': target_column
    }

    return model_info

# 模型保存函数
def save_model(model_info, model_path, metadata_path):
    """Save model and metadata"""
    # 保存模型
    joblib.dump(model_info['model'], model_path)

    # 保存元数据
    metadata = {
        'feature_importance': model_info['feature_importance'],
        'cv_scores': model_info['cv_scores'],
        'prediction_horizon': model_info['prediction_horizon'],
        'target_column': model_info['target_column'],
        'created_at': pd.Timestamp.now().isoformat()
    }

    with open(metadata_path, 'w') as f:
        import json
        json.dump(metadata, f, indent=4)

# 模型加载函数
def load_model(model_path, metadata_path=None):
    """Load model and metadata"""
    # 加载模型
    model = joblib.load(model_path)

    # 加载元数据
    metadata = None
    if metadata_path:
        with open(metadata_path, 'r') as f:
            import json
            metadata = json.load(f)

    return model, metadata

# 预测函数
def predict_price(model, features):
    """Make price predictions"""
    return model.predict(features)
```

### 6.2 模型服务API

```python
# 模型服务API示例

# 导入库
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
import json
from typing import List, Optional

# 导入模型相关函数
from .models import load_model, predict_price, calculate_features

# 创建FastAPI应用
app = FastAPI(title="SimpleTrade AI Model API")

# 模型路径
MODEL_DIR = "models"

# 请求模型
class PredictionRequest(BaseModel):
    symbol: str
    features: dict
    model_type: str = "price_prediction"
    model_version: Optional[str] = "latest"

# 响应模型
class PredictionResponse(BaseModel):
    symbol: str
    prediction: float
    confidence: Optional[float] = None
    model_version: str
    timestamp: str

# 加载模型
def get_model(model_type, model_version="latest"):
    """Load model by type and version"""
    model_path = os.path.join(MODEL_DIR, model_type)

    # 如果请求最新版本，找到最新的模型
    if model_version == "latest":
        versions = [v for v in os.listdir(model_path) if os.path.isdir(os.path.join(model_path, v))]
        versions.sort(reverse=True)
        if not versions:
            raise HTTPException(status_code=404, detail=f"No models found for {model_type}")
        model_version = versions[0]

    # 模型文件路径
    model_file = os.path.join(model_path, model_version, "model.pkl")
    metadata_file = os.path.join(model_path, model_version, "metadata.json")

    # 检查模型文件是否存在
    if not os.path.exists(model_file):
        raise HTTPException(status_code=404, detail=f"Model {model_type} version {model_version} not found")

    # 加载模型
    model, metadata = load_model(model_file, metadata_file if os.path.exists(metadata_file) else None)

    return model, metadata, model_version

# 预测端点
@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make predictions using the model"""
    try:
        # 加载模型
        model, metadata, model_version = get_model(request.model_type, request.model_version)

        # 准备特征
        features_df = pd.DataFrame([request.features])

        # 进行预测
        prediction = predict_price(model, features_df)[0]

        # 返回结果
        return PredictionResponse(
            symbol=request.symbol,
            prediction=float(prediction),
            model_version=model_version,
            timestamp=pd.Timestamp.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 模型信息端点
@app.get("/models/{model_type}")
async def get_model_info(model_type: str, version: str = "latest"):
    """Get model information"""
    try:
        # 加载模型元数据
        _, metadata, model_version = get_model(model_type, version)

        # 返回元数据
        return {
            "model_type": model_type,
            "model_version": model_version,
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 7. 修订历史

| 版本 | 日期 | 描述 | 作者 |
|-----|------|------|------|
| 0.1 | 2023-10-15 | 初稿 | AI助手 |
