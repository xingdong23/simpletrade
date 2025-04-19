<template>
  <div>
    <!-- 顶部标签导航 -->
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 基础策略标签页 -->
      <el-tab-pane label="基础策略" name="basic-strategies" v-loading="strategiesLoading">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">基础策略</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-input
                placeholder="搜索策略..."
                prefix-icon="el-icon-search"
                style="width: 200px; margin-right: 10px;"
              ></el-input>
              <el-select placeholder="所有类型" style="width: 150px;">
                <el-option label="所有类型" value="all"></el-option>
                <!-- TODO: Populate types dynamically if needed -->
              </el-select>
            </el-col>
          </el-row>
        </div>

        <!-- 策略卡片列表 - Modified to use v-for -->
        <el-row :gutter="20">
          <!-- Loop through fetched strategies -->
          <el-col v-if="allStrategies.length === 0 && !strategiesLoading" :span="24" style="text-align: center; color: #909399; padding: 40px 0;">
             暂无策略数据
          </el-col>
          <el-col v-for="strategy in allStrategies" :key="strategy.id" :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
             <el-card shadow="hover" class="strategy-card">
               <div class="strategy-card-content">
                 <div class="strategy-card-header">
                   <h3 class="strategy-title">{{ strategy.name }}</h3>
                   <!-- Display category or type from API data -->
                   <el-tag size="small" type="primary" v-if="strategy.category">{{ strategy.category }}</el-tag>
                   <el-tag size="small" type="info" v-else-if="strategy.type">{{ strategy.type }}</el-tag>
                 </div>
                 <p class="strategy-description">{{ strategy.description || '暂无描述' }}</p>
                 <!-- Simplified display - metrics/complexity/resources from mock data are removed -->
                 <!-- Add back if API provides these -->
                <!-- <div class="strategy-metrics"> ... </div> -->
                <!-- <div class="strategy-complexity"> ... </div> -->
                <!-- <div class="strategy-resources"> ... </div> -->
                 <div class="strategy-actions">
                   <el-button type="primary" size="small" @click="navigateToDetail(strategy.id)">查看详情</el-button>
                   <el-button size="small">使用策略</el-button> <!-- TODO: Implement 'Use Strategy' logic -->
                 </div>
               </div>
             </el-card>
          </el-col>

          <!-- Original hardcoded cards removed -->
          <!-- <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;"> ... </el-col> -->
          <!-- ... more hardcoded cards ... -->

        </el-row>
      </el-tab-pane>

      <!-- 高级策略标签页 -->
      <!-- TODO: Apply similar v-for logic here if needed, potentially filtering allStrategies -->
      <el-tab-pane label="高级策略" name="advanced-strategies">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">高级策略</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-input
                placeholder="搜索策略..."
                prefix-icon="el-icon-search"
                style="width: 200px; margin-right: 10px;"
              ></el-input>
              <el-select placeholder="所有类型" style="width: 150px;">
                <el-option label="所有类型" value="all"></el-option>
                <el-option label="多因子策略" value="multi-factor"></el-option>
                <el-option label="AI策略" value="ai"></el-option>
                <el-option label="组合策略" value="portfolio"></el-option>
              </el-select>
            </el-col>
          </el-row>
        </div>

        <!-- 高级策略卡片列表 -->
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
            <el-card shadow="hover" class="strategy-card">
              <div class="strategy-card-content">
                <div class="strategy-card-header">
                  <h3 class="strategy-title">可视化AI策略</h3>
                  <el-tag size="small" type="danger">AI策略</el-tag>
                </div>
                <p class="strategy-description">训练AI模型进行未来因子权重预测，以期增强策略收益。</p>
                <div class="strategy-metrics">
                  <span class="metric">胜率: <span class="metric-value positive">62%</span></span>
                  <span class="metric">年化收益: <span class="metric-value positive">32.5%</span></span>
                </div>
                <div class="strategy-complexity">
                  <span>复杂度: <el-rate :value="4" disabled text-color="#ff9900" score-template="{value}"></el-rate></span>
                </div>
                <div class="strategy-actions">
                  <el-button type="primary" size="small" @click="navigateToDetail('ai-strategy1')">查看详情</el-button>
                  <el-button size="small">使用策略</el-button>
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
            <el-card shadow="hover" class="strategy-card">
              <div class="strategy-card-content">
                <div class="strategy-card-header">
                  <h3 class="strategy-title">多因子线性策略</h3>
                  <el-tag size="small" type="warning">多因子策略</el-tag>
                </div>
                <p class="strategy-description">通过预计算因子权重，结合多因子线性组合实现选股和排序。</p>
                <div class="strategy-metrics">
                  <span class="metric">胜率: <span class="metric-value positive">59%</span></span>
                  <span class="metric">年化收益: <span class="metric-value positive">26.8%</span></span>
                </div>
                <div class="strategy-complexity">
                  <span>复杂度: <el-rate :value="3" disabled text-color="#ff9900" score-template="{value}"></el-rate></span>
                </div>
                <div class="strategy-actions">
                  <el-button type="primary" size="small" @click="navigateToDetail('multi-factor1')">查看详情</el-button>
                  <el-button size="small">使用策略</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 组件库标签页 -->
      <el-tab-pane label="组件库" name="component-library">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">组件库</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-input
                placeholder="搜索组件..."
                prefix-icon="el-icon-search"
                style="width: 200px; margin-right: 10px;"
              ></el-input>
            </el-col>
          </el-row>
        </div>

        <!-- 组件库子标签页 -->
        <el-tabs v-model="componentActiveTab" type="card" class="component-tabs">
          <el-tab-pane label="因子库" name="factor-library">
            <div style="margin-bottom: 20px;">
              <el-row type="flex" justify="space-between" align="middle">
                <el-col :span="12">
                  <h3 style="font-size: 18px; font-weight: 600; margin: 0;">因子库</h3>
                </el-col>
                <el-col :span="12" style="text-align: right;">
                  <el-select placeholder="因子类型" style="width: 150px;">
                    <el-option label="所有类型" value="all"></el-option>
                    <el-option label="技术因子" value="technical"></el-option>
                    <el-option label="基本面因子" value="fundamental"></el-option>
                    <el-option label="情绪因子" value="sentiment"></el-option>
                    <el-option label="AI因子" value="ai"></el-option>
                  </el-select>
                </el-col>
              </el-row>
            </div>

            <!-- 因子卡片列表 -->
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
                <el-card shadow="hover" class="strategy-card">
                  <div class="strategy-card-content">
                    <div class="strategy-card-header">
                      <h3 class="strategy-title">RSI动量因子</h3>
                      <el-tag size="small" type="success">技术因子</el-tag>
                    </div>
                    <p class="strategy-description">相对强弱指标(RSI)的动量因子，用于捕捉价格超买和超卖区域。</p>
                    <div class="strategy-metrics">
                      <span class="metric">信息比: <span class="metric-value positive">0.65</span></span>
                      <span class="metric">有效期: <span class="metric-value">3个月</span></span>
                    </div>
                    <div class="strategy-actions">
                      <el-button type="primary" size="small">查看详情</el-button>
                      <el-button size="small">使用因子</el-button>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="选股器" name="stock-picker">
            <div style="margin-bottom: 20px;">
              <el-row type="flex" justify="space-between" align="middle">
                <el-col :span="12">
                  <h3 style="font-size: 18px; font-weight: 600; margin: 0;">选股器</h3>
                </el-col>
                <el-col :span="12" style="text-align: right;">
                  <el-select placeholder="所有类型" style="width: 150px;">
                    <el-option label="所有类型" value="all"></el-option>
                    <el-option label="基本面选股" value="fundamental"></el-option>
                    <el-option label="技术面选股" value="technical"></el-option>
                    <el-option label="量化因子" value="factor"></el-option>
                    <el-option label="行业轮动" value="industry"></el-option>
                  </el-select>
                </el-col>
              </el-row>
            </div>

        <!-- 选股器卡片列表 -->
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
            <el-card shadow="hover" class="strategy-card">
              <div class="strategy-card-content">
                <div class="strategy-card-header">
                  <h3 class="strategy-title">价值低估选股</h3>
                  <el-tag size="small" type="success">基本面选股</el-tag>
                </div>
                <p class="strategy-description">基于市盈率、市净率等指标的低估值选股策略。</p>
                <div class="strategy-metrics">
                  <span class="metric">年化收益: <span class="metric-value positive">18.5%</span></span>
                  <span class="metric">最大回撤: <span class="metric-value negative">25.3%</span></span>
                </div>
                <div class="strategy-actions">
                  <el-button type="primary" size="small">查看详情</el-button>
                  <el-button size="small">使用选股器</el-button>
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
            <el-card shadow="hover" class="strategy-card">
              <div class="strategy-card-content">
                <div class="strategy-card-header">
                  <h3 class="strategy-title">动量突破选股</h3>
                  <el-tag size="small" type="warning">技术面选股</el-tag>
                </div>
                <p class="strategy-description">基于价格突破和成交量放大的技术面选股策略。</p>
                <div class="strategy-metrics">
                  <span class="metric">年化收益: <span class="metric-value positive">22.3%</span></span>
                  <span class="metric">最大回撤: <span class="metric-value negative">32.1%</span></span>
                </div>
                <div class="strategy-actions">
                  <el-button type="primary" size="small">查看详情</el-button>
                  <el-button size="small">使用选股器</el-button>
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
            <el-card shadow="hover" class="strategy-card">
              <div class="strategy-card-content">
                <div class="strategy-card-header">
                  <h3 class="strategy-title">多因子选股</h3>
                  <el-tag size="small" type="danger">量化因子</el-tag>
                </div>
                <p class="strategy-description">结合多个量化因子的综合选股策略，包括动量、价值、质量等。</p>
                <div class="strategy-metrics">
                  <span class="metric">年化收益: <span class="metric-value positive">25.8%</span></span>
                  <span class="metric">最大回撤: <span class="metric-value negative">28.5%</span></span>
                </div>
                <div class="strategy-actions">
                  <el-button type="primary" size="small">查看详情</el-button>
                  <el-button size="small">使用选股器</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="交易战法" name="trading-tactics">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h3 style="font-size: 18px; font-weight: 600; margin: 0;">交易战法</h3>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-select placeholder="所有类型" style="width: 150px;">
                <el-option label="所有类型" value="all"></el-option>
                <el-option label="缠论战法" value="chan"></el-option>
                <el-option label="道氏理论" value="dow"></el-option>
                <el-option label="波浪理论" value="wave"></el-option>
                <el-option label="古典技术分析" value="classic"></el-option>
              </el-select>
            </el-col>
          </el-row>
        </div>
        <!-- 交易战法卡片列表 -->
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
            <el-card shadow="hover" class="strategy-card">
              <div class="strategy-card-content">
                <div class="strategy-card-header">
                  <h3 class="strategy-title">缠论三买战法</h3>
                  <el-tag size="small" type="warning">缠论战法</el-tag>
                </div>
                <p class="strategy-description">基于缠论理论的三买点交易战法，精准把握底部买入时机。</p>
                <div class="strategy-metrics">
                  <span class="metric">胜率: <span class="metric-value positive">65%</span></span>
                  <span class="metric">年化收益: <span class="metric-value positive">28.5%</span></span>
                </div>
                <div class="strategy-actions">
                  <el-button type="primary" size="small">查看详情</el-button>
                  <el-button size="small">使用战法</el-button>
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
            <el-card shadow="hover" class="strategy-card">
              <div class="strategy-card-content">
                <div class="strategy-card-header">
                  <h3 class="strategy-title">道氏理论确认战法</h3>
                  <el-tag size="small" type="danger">道氏理论</el-tag>
                </div>
                <p class="strategy-description">基于道氏理论的价格与成交量相互确认的交易战法。</p>
                <div class="strategy-metrics">
                  <span class="metric">胜率: <span class="metric-value positive">58%</span></span>
                  <span class="metric">年化收益: <span class="metric-value positive">24.3%</span></span>
                </div>
                <div class="strategy-actions">
                  <el-button type="primary" size="small">查看详情</el-button>
                  <el-button size="small">使用战法</el-button>
                </div>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
            <el-card shadow="hover" class="strategy-card">
              <div class="strategy-card-content">
                <div class="strategy-card-header">
                  <h3 class="strategy-title">波浪理论交易战法</h3>
                  <el-tag size="small" type="primary">波浪理论</el-tag>
                </div>
                <p class="strategy-description">基于艾略特波浪理论的交易战法，精准把握市场节奏。</p>
                <div class="strategy-metrics">
                  <span class="metric">胜率: <span class="metric-value positive">62%</span></span>
                  <span class="metric">年化收益: <span class="metric-value positive">26.7%</span></span>
                </div>
                <div class="strategy-actions">
                  <el-button type="primary" size="small">查看详情</el-button>
                  <el-button size="small">使用战法</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
        </el-tabs>
      </el-tab-pane>

      <el-tab-pane label="策略构建器" name="builder">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">策略构建器</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-radio-group v-model="builderMode" size="small">
                <el-radio-button label="visual">可视化构建器</el-radio-button>
                <el-radio-button label="code">代码编辑器</el-radio-button>
              </el-radio-group>
            </el-col>
          </el-row>
        </div>

        <!-- 可视化构建器 -->
        <el-card shadow="hover" v-if="builderMode === 'visual'">
          <div slot="header">
            <h3 style="margin: 0; font-size: 18px; font-weight: 600;">可视化构建器</h3>
            <p style="margin: 10px 0 0; color: #606266;">使用可视化构建器创建自定义策略，无需编写代码。</p>
          </div>

          <el-form label-position="top" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="选择策略类型">
                  <el-radio-group v-model="strategyType">
                    <el-radio label="cta">技术指标策略</el-radio>
                    <el-radio label="factor">因子策略</el-radio>
                    <el-radio label="ai">AI策略</el-radio>
                    <el-radio label="portfolio">组合策略</el-radio>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="选择指标/因子">
                  <el-checkbox-group v-model="indicators">
                    <el-checkbox label="ma">移动平均线 (MA)</el-checkbox>
                    <el-checkbox label="rsi">相对强弱指标 (RSI)</el-checkbox>
                    <el-checkbox label="macd">MACD</el-checkbox>
                    <el-checkbox label="bollinger">布林带 (Bollinger Bands)</el-checkbox>
                    <el-checkbox label="kdj">KDJ指标</el-checkbox>
                    <el-checkbox label="volume">成交量分析</el-checkbox>
                    <el-checkbox label="momentum" v-if="strategyType === 'factor'">动量因子</el-checkbox>
                    <el-checkbox label="value" v-if="strategyType === 'factor'">价值因子</el-checkbox>
                    <el-checkbox label="quality" v-if="strategyType === 'factor'">质量因子</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="策略名称">
                  <el-input v-model="strategyName" placeholder="输入策略名称"></el-input>
                </el-form-item>

                <el-form-item label="MA周期" v-if="indicators.includes('ma')">
                  <el-input-number v-model="maPeriod" :min="1" :max="200"></el-input-number>
                </el-form-item>

                <el-form-item label="RSI周期" v-if="indicators.includes('rsi')">
                  <el-input-number v-model="rsiPeriod" :min="1" :max="100"></el-input-number>
                </el-form-item>

                <el-form-item label="仓位大小 (%)">
                  <el-slider v-model="positionSize" :min="1" :max="100" :step="1" show-input></el-slider>
                </el-form-item>

                <el-form-item>
                  <el-button type="primary">创建策略</el-button>
                  <el-button>预览代码</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>

        <!-- 代码编辑器 -->
        <el-card shadow="hover" v-else>
          <div slot="header">
            <h3 style="margin: 0; font-size: 18px; font-weight: 600;">代码编辑器</h3>
            <p style="margin: 10px 0 0; color: #606266;">使用代码编辑器创建自定义策略，可实现更复杂的逻辑。</p>
          </div>

          <el-form label-position="top">
            <el-form-item label="策略名称">
              <el-input v-model="strategyName" placeholder="输入策略名称"></el-input>
            </el-form-item>

            <el-form-item label="策略代码">
              <div style="border: 1px solid #dcdfe6; border-radius: 4px; height: 400px; padding: 10px; background-color: #f5f7fa; font-family: monospace; overflow: auto;">
                <pre style="margin: 0;"># 策略模板
from vnpy.trader.constant import Direction
from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData
)

class MyStrategy(CtaTemplate):
    """自定义策略"""

    # 策略参数
    fast_window = 10
    slow_window = 20
    rsi_window = 14
    rsi_level = 30

    # 变量初始化
    fast_ma = 0.0
    slow_ma = 0.0
    ma_trend = 0
    rsi_value = 0.0

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

    def on_init(self):
        """Initialize strategy variables."""
        self.write_log("Strategy initialized")
        self.load_bar(10)

    def on_bar(self, bar: BarData):
        """Strategy logic on bar data update."""
        # 更新技术指标
        # 实现交易逻辑
        pass</pre>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button type="primary">保存策略</el-button>
              <el-button>运行回测</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="我的策略" name="my-strategies" v-loading="myStrategiesLoading">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">我的策略</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="primary" icon="el-icon-plus">新建策略</el-button>
            </el-col>
          </el-row>
        </div>

        <el-table :data="myStrategiesList" style="width: 100%" border>
          <el-table-column prop="name" label="策略名称" width="180"></el-table-column>
          <el-table-column prop="type" label="类型" width="120">
            <template slot-scope="scope">
              <el-tag size="small">{{ scope.row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createTime" label="创建时间" width="180"></el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template slot-scope="scope">
              <el-tag 
                :type="scope.row.status === '运行中' ? 'success' : scope.row.status === '已初始化' ? 'warning' : scope.row.status === '未加载' ? 'info' : 'danger'" 
                size="small"
              >
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template slot-scope="scope">
              <el-button size="mini" type="text" @click="navigateToDetail(scope.row.id)">查看</el-button>
              <el-button size="mini" type="text" @click="handleBacktest(scope.row)">回测</el-button>
              <el-button size="mini" type="text" @click="handleOptimize(scope.row)">优化</el-button>
              <el-button
                size="mini"
                type="text"
                :style="{ color: scope.row.status === '运行中' ? '#F56C6C' : '#67C23A' }" 
                @click="handleAction(scope.row)"
              >
                {{ scope.row.status === '运行中' ? '停止' : '启动' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    <!-- 策略详情对话框 -->
    <el-dialog :title="'策略详情: ' + (currentStrategy ? currentStrategy.name : '')" :visible.sync="strategyDetailVisible" width="80%">
      <el-tabs v-model="detailActiveTab">
      <!-- 策略信息标签页 -->
      <el-tab-pane label="策略信息" name="info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="策略名称">{{ currentStrategy ? currentStrategy.name : '' }}</el-descriptions-item>
          <el-descriptions-item label="策略类型">{{ currentStrategy ? currentStrategy.type : '' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentStrategy ? currentStrategy.createTime : '' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentStrategy && currentStrategy.status === '运行中' ? 'success' : currentStrategy && currentStrategy.status === '待运行' ? 'warning' : 'info'" size="small">
              {{ currentStrategy ? currentStrategy.status : '' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 20px;">
          <h3>策略描述</h3>
          <p>这是一个基于技术指标的量化交易策略，使用移动平均线、RSI和其他指标来生成交易信号。</p>
        </div>

        <div style="margin-top: 20px;">
          <h3>策略参数</h3>
          <el-form :model="strategyParams" label-width="120px">
            <el-form-item label="短周期移动平均线">
              <el-input-number v-model="strategyParams.shortPeriod" :min="1" :max="100"></el-input-number>
            </el-form-item>
            <el-form-item label="长周期移动平均线">
              <el-input-number v-model="strategyParams.longPeriod" :min="10" :max="200"></el-input-number>
            </el-form-item>
            <el-form-item label="RSI周期">
              <el-input-number v-model="strategyParams.rsiPeriod" :min="1" :max="100"></el-input-number>
            </el-form-item>
            <el-form-item label="RSI超买线">
              <el-input-number v-model="strategyParams.rsiOverbought" :min="50" :max="100"></el-input-number>
            </el-form-item>
            <el-form-item label="RSI超卖线">
              <el-input-number v-model="strategyParams.rsiOversold" :min="0" :max="50"></el-input-number>
            </el-form-item>
            <el-form-item label="仓位大小 (%)">
              <el-slider v-model="strategyParams.positionSize" :min="1" :max="100" :step="1" show-input></el-slider>
            </el-form-item>
            <el-form-item label="止损比例 (%)">
              <el-input-number v-model="strategyParams.stopLoss" :min="0.5" :max="20" :step="0.5"></el-input-number>
            </el-form-item>
            <el-form-item label="止盈比例 (%)">
              <el-input-number v-model="strategyParams.takeProfit" :min="0.5" :max="50" :step="0.5"></el-input-number>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveStrategyParams">保存参数</el-button>
              <el-button type="success" @click="detailActiveTab = 'backtest'">运行回测</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 回测标签页 -->
      <el-tab-pane label="回测" name="backtest">
        <el-form :inline="true" class="demo-form-inline" style="margin-bottom: 20px;">
          <el-form-item label="回测起始日期">
            <el-date-picker v-model="backtestParams.startDate" type="date" placeholder="选择日期"></el-date-picker>
          </el-form-item>
          <el-form-item label="回测结束日期">
            <el-date-picker v-model="backtestParams.endDate" type="date" placeholder="选择日期"></el-date-picker>
          </el-form-item>
          <el-form-item label="初始资金">
            <el-input-number v-model="backtestParams.initialCapital" :min="10000" :step="10000"></el-input-number>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="runBacktest">运行回测</el-button>
          </el-form-item>
        </el-form>

        <!-- 回测结果 -->
        <div v-if="backtestResult.hasResult">
          <el-divider content-position="left">回测结果</el-divider>

          <!-- 回测指标 -->
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="6">
              <el-card shadow="hover">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">总收益率</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #67C23A; margin: 0;">+{{ backtestResult.totalReturn }}%</p>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">年化收益率</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #67C23A; margin: 0;">+{{ backtestResult.annualReturn }}%</p>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">最大回撤率</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #F56C6C; margin: 0;">{{ backtestResult.maxDrawdown }}%</p>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">胜率</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #409EFF; margin: 0;">{{ backtestResult.winRate }}%</p>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 收益曲线图 -->
          <el-card shadow="hover" style="margin-bottom: 20px;">
            <div slot="header">
              <span>收益曲线</span>
            </div>
            <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: #909399;">
              <i class="el-icon-data-line" style="font-size: 24px; margin-right: 10px;"></i>
              收益曲线图（这里将显示图表）
            </div>
          </el-card>

          <!-- 交易记录 -->
          <el-card shadow="hover">
            <div slot="header">
              <span>交易记录</span>
            </div>
            <el-table :data="backtestResult.trades" style="width: 100%">
              <el-table-column prop="date" label="日期" width="180"></el-table-column>
              <el-table-column prop="type" label="类型" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.type === '买入' ? 'success' : 'danger'" size="small">{{ scope.row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="价格" width="120"></el-table-column>
              <el-table-column prop="quantity" label="数量" width="120"></el-table-column>
              <el-table-column prop="profit" label="盈亏" width="120">
                <template slot-scope="scope">
                  <span :style="{ color: scope.row.profit >= 0 ? '#67C23A' : '#F56C6C' }">
                    {{ scope.row.profit >= 0 ? '+' : '' }}{{ scope.row.profit }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <!-- 部署到实盘按钮 -->
          <div style="margin-top: 20px; text-align: center;">
            <el-button type="success" @click="deployToLive">部署到实盘</el-button>
          </div>
        </div>
        <div v-else style="text-align: center; padding: 50px 0;">
          <i class="el-icon-data-analysis" style="font-size: 48px; color: #909399; margin-bottom: 20px;"></i>
          <p>还没有运行回测，请点击"运行回测"按钮开始回测。</p>
        </div>
      </el-tab-pane>

      <!-- 参数优化标签页 -->
      <el-tab-pane label="参数优化" name="optimize">
        <el-form :inline="true" class="demo-form-inline" style="margin-bottom: 20px;">
          <el-form-item label="优化目标">
            <el-select v-model="optimizeParams.target" placeholder="选择优化目标">
              <el-option label="总收益率" value="totalReturn"></el-option>
              <el-option label="复合收益/最大回撤" value="returnDrawdownRatio"></el-option>
              <el-option label="复合胜率/最大回撤" value="winRateDrawdownRatio"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="优化参数">
            <el-select v-model="optimizeParams.parameters" multiple placeholder="选择要优化的参数">
              <el-option label="短周期移动平均线" value="shortPeriod"></el-option>
              <el-option label="长周期移动平均线" value="longPeriod"></el-option>
              <el-option label="RSI周期" value="rsiPeriod"></el-option>
              <el-option label="RSI超买线" value="rsiOverbought"></el-option>
              <el-option label="RSI超卖线" value="rsiOversold"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="runOptimization">运行优化</el-button>
          </el-form-item>
        </el-form>

        <!-- 优化结果 -->
        <div v-if="optimizeResult.hasResult">
          <el-divider content-position="left">优化结果</el-divider>

          <!-- 最佳参数组合 -->
          <el-card shadow="hover" style="margin-bottom: 20px;">
            <div slot="header">
              <span>最佳参数组合</span>
            </div>
            <el-descriptions :column="3" border>
              <el-descriptions-item v-for="(value, key) in optimizeResult.bestParams" :key="key" :label="key">
                {{ value }}
              </el-descriptions-item>
            </el-descriptions>
            <div style="margin-top: 20px; text-align: right;">
              <el-button type="primary" @click="applyOptimizedParams">应用最佳参数</el-button>
            </div>
          </el-card>

          <!-- 参数组合对比 -->
          <el-card shadow="hover">
            <div slot="header">
              <span>参数组合对比</span>
            </div>
            <el-table :data="optimizeResult.paramSets" style="width: 100%">
              <el-table-column v-for="(param, index) in optimizeParams.parameters" :key="index" :prop="param" :label="param" width="120"></el-table-column>
              <el-table-column prop="totalReturn" label="总收益率" width="120">
                <template slot-scope="scope">
                  <span :style="{ color: scope.row.totalReturn >= 0 ? '#67C23A' : '#F56C6C' }">
                    {{ scope.row.totalReturn >= 0 ? '+' : '' }}{{ scope.row.totalReturn }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="maxDrawdown" label="最大回撤率" width="120">
                <template slot-scope="scope">
                  <span style="color: #F56C6C;">{{ scope.row.maxDrawdown }}%</span>
                </template>
              </el-table-column>
              <el-table-column prop="winRate" label="胜率" width="120">
                <template slot-scope="scope">
                  <span>{{ scope.row.winRate }}%</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template slot-scope="scope">
                  <el-button size="mini" type="text" @click="applyParamSet(scope.row)">应用</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
        <div v-else style="text-align: center; padding: 50px 0;">
          <i class="el-icon-cpu" style="font-size: 48px; color: #909399; margin-bottom: 20px;"></i>
          <p>还没有运行优化，请选择参数并点击"运行优化"按钮。</p>
        </div>
      </el-tab-pane>

      <!-- 实盘交易标签页 -->
      <el-tab-pane label="实盘交易" name="live">
        <div v-if="currentStrategy && currentStrategy.status === '运行中'">
          <!-- 实盘交易状态 -->
          <el-card shadow="hover" style="margin-bottom: 20px;">
            <div slot="header">
              <span>实盘交易状态</span>
            </div>
            <el-row :gutter="20">
              <el-col :span="6">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">运行时间</h3>
                  <p style="font-size: 18px; font-weight: 600; color: #303133; margin: 0;">3天 5小时</p>
                </div>
              </el-col>
              <el-col :span="6">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">当前收益</h3>
                  <p style="font-size: 18px; font-weight: 600; color: #67C23A; margin: 0;">+2.5%</p>
                </div>
              </el-col>
              <el-col :span="6">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">持仓数量</h3>
                  <p style="font-size: 18px; font-weight: 600; color: #303133; margin: 0;">200股</p>
                </div>
              </el-col>
              <el-col :span="6">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">交易次数</h3>
                  <p style="font-size: 18px; font-weight: 600; color: #303133; margin: 0;">8次</p>
                </div>
              </el-col>
            </el-row>
          </el-card>

          <!-- 实时收益曲线 -->
          <el-card shadow="hover" style="margin-bottom: 20px;">
            <div slot="header">
              <span>实时收益曲线</span>
            </div>
            <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: #909399;">
              <i class="el-icon-data-line" style="font-size: 24px; margin-right: 10px;"></i>
              实时收益曲线（这里将显示图表）
            </div>
          </el-card>

          <!-- 最近交易 -->
          <el-card shadow="hover">
            <div slot="header">
              <span>最近交易</span>
            </div>
            <el-table :data="liveTradeRecords" style="width: 100%">
              <el-table-column prop="date" label="日期" width="180"></el-table-column>
              <el-table-column prop="type" label="类型" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.type === '买入' ? 'success' : 'danger'" size="small">{{ scope.row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="价格" width="120"></el-table-column>
              <el-table-column prop="quantity" label="数量" width="120"></el-table-column>
              <el-table-column prop="amount" label="金额" width="150"></el-table-column>
              <el-table-column prop="status" label="状态" width="120">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.status === '已成交' ? 'success' : scope.row.status === '已取消' ? 'info' : 'warning'" size="small">{{ scope.row.status }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
        <div v-else style="text-align: center; padding: 50px 0;">
          <i class="el-icon-warning-outline" style="font-size: 48px; color: #E6A23C; margin-bottom: 20px;"></i>
          <p>策略当前未在实盘运行。请先运行回测，然后部署到实盘。</p>
          <el-button type="primary" @click="detailActiveTab = 'backtest'">运行回测</el-button>
        </div>
      </el-tab-pane>
    </el-tabs>
  </el-dialog>
  </div>
</template>

<script>
// 导入 API 函数
import { getStrategies, getUserStrategies } from '@/api/strategies'

export default {
  name: 'StrategyCenterView',
  data() {
    return {
      // Loading state for strategies
      strategiesLoading: false,
      // Array to store fetched strategies
      allStrategies: [],
      // --- Add data for My Strategies ---
      myStrategiesLoading: false,
      myStrategiesList: [], // 用于存储从API获取的用户策略
      // Hardcoded user ID for now
      currentUserId: 1, 
      // --- Existing data properties below ---
      activeTab: 'basic-strategies',
      // 所有标签页
      tabOptions: [
        { name: 'basic-strategies', label: '基础策略' },
        { name: 'advanced-strategies', label: '高级策略' },
        { name: 'component-library', label: '组件库' },
        { name: 'builder', label: '策略构建器' },
        { name: 'my-strategies', label: '我的策略' }
      ],
      // 组件库子标签页
      componentActiveTab: 'factor-library',
      componentTabOptions: [
        { name: 'factor-library', label: '因子库' },
        { name: 'stock-picker', label: '选股器' },
        { name: 'trading-tactics', label: '交易战法' }
      ],
      strategyType: 'cta',
      indicators: [],
      strategyName: '',
      maPeriod: 20,
      rsiPeriod: 14,
      positionSize: 10,
      builderMode: 'visual',
      myStrategies: [
        {
          name: '我的双均线策略',
          type: 'CTA策略',
          createTime: '2023-10-15',
          status: '运行中'
        },
        {
          name: 'LSTM预测模型',
          type: 'AI策略',
          createTime: '2023-10-10',
          status: '待运行'
        }
      ],
      // 策略详情对话框
      strategyDetailVisible: false,
      currentStrategy: null,
      detailActiveTab: 'info',

      // 策略参数
      strategyParams: {
        shortPeriod: 5,
        longPeriod: 20,
        rsiPeriod: 14,
        rsiOverbought: 70,
        rsiOversold: 30,
        positionSize: 10,
        stopLoss: 5,
        takeProfit: 15
      },

      // 回测参数
      backtestParams: {
        startDate: new Date(new Date().getTime() - 90 * 24 * 60 * 60 * 1000), // 90天前
        endDate: new Date(),
        initialCapital: 100000
      },

      // 回测结果
      backtestResult: {
        hasResult: false,
        totalReturn: 0,
        annualReturn: 0,
        maxDrawdown: 0,
        winRate: 0,
        trades: []
      },

      // 优化参数
      optimizeParams: {
        target: 'totalReturn',
        parameters: []
      },

      // 优化结果
      optimizeResult: {
        hasResult: false,
        bestParams: {},
        paramSets: []
      },

      // 实盘交易记录
      liveTradeRecords: []
    }
  },
  // Add created hook to fetch data when component is created
  created() {
    this.fetchStrategies();
    this.fetchMyStrategies();
  },
  methods: {
    // --- Add method to fetch strategies ---
    fetchStrategies() {
      this.strategiesLoading = true;
      getStrategies() // Fetch all strategies (no filters/pagination for now)
        .then(response => {
          if (response.data && response.data.success) {
            this.allStrategies = response.data.data || []; // Ensure it's an array
            this.$message.success('策略列表已加载');
          } else {
            this.$message.error(response.data.message || '加载策略列表失败');
            this.allStrategies = []; // Clear on failure
          }
        })
        .catch(error => {
          console.error('加载策略列表错误:', error);
          this.$message.error('网络错误，无法加载策略列表');
          this.allStrategies = []; // Clear on error
        })
        .finally(() => {
          this.strategiesLoading = false;
        });
    },
    // --- Add method to fetch user strategies ---
    fetchMyStrategies() {
      this.myStrategiesLoading = true;
      // 使用硬编码的用户ID调用API
      getUserStrategies(this.currentUserId)
        .then(response => {
          if (response.data && response.data.success) {
            this.myStrategiesList = response.data.data || [];
            // 可以选择性地添加消息提示
            // this.$message.success('我的策略列表已加载');
          } else {
            this.$message.error(response.data.message || '加载我的策略列表失败');
            this.myStrategiesList = [];
          }
        })
        .catch(error => {
          console.error('加载我的策略列表错误:', error);
          this.$message.error('网络错误，无法加载我的策略列表');
          this.myStrategiesList = [];
        })
        .finally(() => {
          this.myStrategiesLoading = false;
        });
    },
    // --- Existing methods below ---
    // 导航到策略详情页面
    navigateToDetail(strategyId) {
      // TODO: This needs actual strategy ID from fetched data
      // For now, keep the placeholder logic or adapt if IDs are available
      const idToUse = typeof strategyId === 'object' ? strategyId.id : strategyId; // Handle potential object passing
      this.$router.push(`/strategy-detail/${idToUse}`);
      // Original line: this.$router.push(`/strategy-detail/${strategyId}`);
    },

    // 查看策略详情
    handleView(row) {
      this.currentStrategy = JSON.parse(JSON.stringify(row));
      this.strategyDetailVisible = true;
      this.detailActiveTab = 'info';

      // 模拟加载策略参数
      if (row.name.includes('双均线')) {
        this.strategyParams = {
          shortPeriod: 5,
          longPeriod: 20,
          rsiPeriod: 14,
          rsiOverbought: 70,
          rsiOversold: 30,
          positionSize: 10,
          stopLoss: 5,
          takeProfit: 15
        };
      } else if (row.name.includes('LSTM')) {
        this.strategyParams = {
          shortPeriod: 3,
          longPeriod: 15,
          rsiPeriod: 10,
          rsiOverbought: 75,
          rsiOversold: 25,
          positionSize: 15,
          stopLoss: 3,
          takeProfit: 20
        };
      }

      // 清除之前的回测结果
      this.backtestResult.hasResult = false;
      this.optimizeResult.hasResult = false;
    },

    // 直接运行回测
    handleBacktest(row) {
      this.handleView(row);
      this.detailActiveTab = 'backtest';
    },

    // 直接运行参数优化
    handleOptimize(row) {
      this.handleView(row);
      this.detailActiveTab = 'optimize';
    },

    // 启动/停止策略
    handleAction(row) {
      if (row.status === '运行中') {
        // 停止策略
        this.$confirm('确定要停止该策略吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          // 模拟停止策略
          row.status = '待运行';
          this.$message({
            type: 'success',
            message: `策略 ${row.name} 已停止`
          });
        }).catch(() => {});
      } else {
        // 启动策略
        this.handleView(row);
        this.detailActiveTab = 'backtest';
      }
    },

    // 保存策略参数
    saveStrategyParams() {
      this.$message({
        type: 'success',
        message: '策略参数保存成功'
      });
    },

    // 运行回测
    runBacktest() {
      // 模拟回测过程
      this.$message({
        type: 'info',
        message: '正在运行回测...'
      });

      // 模拟异步回测
      setTimeout(() => {
        // 生成模拟回测结果
        this.backtestResult = {
          hasResult: true,
          totalReturn: 28.5,
          annualReturn: 32.7,
          maxDrawdown: 12.3,
          winRate: 58,
          trades: [
            { date: '2023-10-01', type: '买入', price: '150.25', quantity: '100', profit: 0 },
            { date: '2023-10-05', type: '卖出', price: '155.50', quantity: '100', profit: 525 },
            { date: '2023-10-10', type: '买入', price: '152.75', quantity: '100', profit: 0 },
            { date: '2023-10-15', type: '卖出', price: '158.25', quantity: '100', profit: 550 },
            { date: '2023-10-20', type: '买入', price: '156.50', quantity: '100', profit: 0 },
            { date: '2023-10-25', type: '卖出', price: '153.75', quantity: '100', profit: -275 }
          ]
        };

        this.$message({
          type: 'success',
          message: '回测完成'
        });
      }, 1500);
    },

    // 部署到实盘
    deployToLive() {
      this.$confirm('确定要将策略部署到实盘吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 模拟部署过程
        this.$message({
          type: 'info',
          message: '正在部署策略...'
        });

        setTimeout(() => {
          // 更新策略状态
          if (this.currentStrategy) {
            // 更新当前策略状态
            this.currentStrategy.status = '运行中';

            // 同步更新列表中的策略状态
            const strategy = this.myStrategies.find(s => s.name === this.currentStrategy.name);
            if (strategy) {
              strategy.status = '运行中';
            }

            // 切换到实盘标签页
            this.detailActiveTab = 'live';

            // 生成模拟实盘交易记录
            this.liveTradeRecords = [
              { date: '2023-10-25 09:30:15', type: '买入', price: '156.50', quantity: '100', amount: '15,650.00', status: '已成交' },
              { date: '2023-10-25 10:15:30', type: '卖出', price: '157.25', quantity: '50', amount: '7,862.50', status: '已成交' },
              { date: '2023-10-25 14:20:45', type: '买入', price: '155.75', quantity: '50', amount: '7,787.50', status: '已成交' }
            ];

            this.$message({
              type: 'success',
              message: `策略 ${this.currentStrategy.name} 已成功部署到实盘`
            });
          }
        }, 1500);
      }).catch(() => {});
    },

    // 运行参数优化
    runOptimization() {
      if (!this.optimizeParams.parameters.length) {
        this.$message({
          type: 'warning',
          message: '请选择要优化的参数'
        });
        return;
      }

      // 模拟优化过程
      this.$message({
        type: 'info',
        message: '正在运行参数优化...'
      });

      // 模拟异步优化
      setTimeout(() => {
        // 生成模拟优化结果
        this.optimizeResult = {
          hasResult: true,
          bestParams: {
            shortPeriod: 3,
            longPeriod: 15,
            rsiPeriod: 12,
            rsiOverbought: 75,
            rsiOversold: 25
          },
          paramSets: [
            { shortPeriod: 3, longPeriod: 15, rsiPeriod: 12, totalReturn: 32.5, maxDrawdown: 10.2, winRate: 62 },
            { shortPeriod: 5, longPeriod: 20, rsiPeriod: 14, totalReturn: 28.5, maxDrawdown: 12.3, winRate: 58 },
            { shortPeriod: 7, longPeriod: 25, rsiPeriod: 16, totalReturn: 25.8, maxDrawdown: 14.5, winRate: 55 },
            { shortPeriod: 3, longPeriod: 20, rsiPeriod: 14, totalReturn: 30.2, maxDrawdown: 11.5, winRate: 60 },
            { shortPeriod: 5, longPeriod: 15, rsiPeriod: 12, totalReturn: 29.7, maxDrawdown: 13.1, winRate: 59 }
          ]
        };

        this.$message({
          type: 'success',
          message: '参数优化完成'
        });
      }, 2000);
    },

    // 应用最佳参数
    applyOptimizedParams() {
      // 将最佳参数应用到策略参数
      Object.assign(this.strategyParams, this.optimizeResult.bestParams);

      this.$message({
        type: 'success',
        message: '已应用最佳参数'
      });

      // 切换到策略信息标签页
      this.detailActiveTab = 'info';
    },

    // 应用特定参数组合
    applyParamSet(paramSet) {
      // 将选中的参数组合应用到策略参数
      Object.keys(paramSet).forEach(key => {
        if (key !== 'totalReturn' && key !== 'maxDrawdown' && key !== 'winRate') {
          this.strategyParams[key] = paramSet[key];
        }
      });

      this.$message({
        type: 'success',
        message: '已应用选中的参数组合'
      });

      // 切换到策略信息标签页
      this.detailActiveTab = 'info';
    }
  }
}
</script>

<style>
.el-tabs__header {
  margin-bottom: 25px;
}

/* 策略卡片统一样式 */
.strategy-card {
  height: 100%;
  transition: all 0.3s;
}

.strategy-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.strategy-card-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.strategy-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.strategy-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}

.strategy-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
  flex-grow: 1;
  min-height: 40px;
}

.strategy-metrics {
  display: flex;
  margin-bottom: 10px;
  font-size: 14px;
  color: #909399;
}

.metric {
  margin-right: 15px;
}

.metric-value {
  font-weight: 500;
}

.metric-value.positive {
  color: #67C23A;
}

.metric-value.negative {
  color: #F56C6C;
}

.strategy-complexity {
  margin-bottom: 10px;
  font-size: 14px;
  color: #909399;
}

.strategy-resources {
  display: flex;
  margin-bottom: 15px;
  font-size: 14px;
  color: #909399;
}

.strategy-actions {
  display: flex;
  justify-content: space-between;
  margin-top: auto;
}

.component-tabs .el-tabs__header {
  margin-bottom: 15px;
}

.component-tabs .el-tabs__nav {
  border-radius: 4px;
}
</style>

<style scoped>
/* 在这里添加组件的局部样式 */
.strategy-card {
  /* 设置最小高度以统一卡片布局 */
  min-height: 300px; /* 您可能需要根据实际内容调整此值 */
  height: 100%; /* 尝试让卡片填满其列的高度 */
  display: flex;
  flex-direction: column;
}

.strategy-card .el-card__body {
  /* 让卡片主体内容区域能够伸缩 */
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding: 15px; /* 可以根据需要调整内边距 */
}

.strategy-card-content {
  /* 假设这是包裹卡片主要内容的 div */
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 将内容推开，使按钮组保持在底部 */
}

.strategy-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.strategy-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  flex-grow: 1; /* 让标题占据多余空间 */
  margin-right: 10px; /* 与标签保持间距 */
}

.strategy-description {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 15px;
  /* 如果描述过长，可以考虑限制行数并显示省略号 */
  /*
  display: -webkit-box;
  -webkit-line-clamp: 3; 
  -webkit-box-orient: vertical;  
  overflow: hidden;
  text-overflow: ellipsis;
  */
}

.strategy-metrics,
.strategy-complexity,
.strategy-resources {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.metric {
  margin-right: 15px;
}

.metric-value {
  font-weight: bold;
}

.metric-value.positive {
  color: #67c23a; /* 绿色表示正向指标 */
}

.metric-value.negative {
  color: #f56c6c; /* 红色表示负向指标 */
}

.strategy-actions {
  margin-top: auto; /* 将按钮组推到底部 */
  padding-top: 10px; /* 与上方内容保持间距 */
  border-top: 1px solid #ebeef5; /* 可选：添加分隔线 */
  text-align: right; /* 让按钮靠右 */
}

.component-tabs > .el-tabs__content {
  padding: 20px;
}

.backtest-section .el-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 400px; /* 为图表设置固定高度 */
}

/* 优化标签页样式 */
.el-tabs--border-card > .el-tabs__header .el-tabs__item.is-active {
    color: #409EFF; /* Element Plus 主题蓝 */
    font-weight: bold;
}

.el-tabs--border-card > .el-tabs__header .el-tabs__item {
    color: #606266;
}

</style>
