<template>
  <div>
    <!-- 顶部标签导航 -->
    <el-tabs v-model="activeTab" type="border-card" @tab-click="handleTabClick">
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
              <el-select
                placeholder="所有基础类型"
                style="width: 150px;"
                v-model="selectedBasicType" 
                @change="filterBasicStrategies" 
                clearable
              >
                <el-option label="所有基础类型" value="all"></el-option>
                <el-option
                  v-for="type in basicStrategyTypes" 
                  :key="type"
                  :label="type"
                  :value="type"
                ></el-option>
              </el-select>
            </el-col>
          </el-row>
        </div>

        <!-- 策略卡片列表 - 遍历 filteredBasicStrategies -->
        <el-row :gutter="20" type="flex" style="flex-wrap: wrap;">
          <el-col v-if="filteredBasicStrategies.length === 0 && !strategiesLoading" :span="24" style="text-align: center; color: #909399; padding: 40px 0;">
             暂无符合条件的基础策略
          </el-col>
          <el-col v-for="strategy in filteredBasicStrategies" :key="strategy.id" :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
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
                   <!-- <el-button size="small">使用策略</el-button> --> <!-- 模板页不应有"使用" -->
                 </div>
               </div>
             </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 高级策略标签页 -->
      <el-tab-pane label="高级策略 (AI)" name="advanced-strategies" v-loading="strategiesLoading">
         <!-- ... (可以添加类似的搜索和过滤, 如果高级策略多的话) ... -->
         <div style="margin-bottom: 20px;">
            <el-row type="flex" justify="space-between" align="middle">
                 <el-col :span="12">
                    <h2 style="font-size: 20px; font-weight: 600; margin: 0;">高级策略 (AI)</h2>
                 </el-col>
                 <!-- Optional Filters -->
            </el-row>
         </div>
        <!-- 高级策略卡片列表 - 遍历 advancedStrategies -->
        <el-row :gutter="20" type="flex" style="flex-wrap: wrap;">
            <el-col v-if="advancedStrategies.length === 0 && !strategiesLoading" :span="24" style="text-align: center; color: #909399; padding: 40px 0;">
                 暂无高级策略数据
            </el-col>
           <el-col v-for="strategy in advancedStrategies" :key="strategy.id" :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
             <el-card shadow="hover" class="strategy-card">
               <div class="strategy-card-content">
                 <div class="strategy-card-header">
                   <h3 class="strategy-title">{{ strategy.name }}</h3>
                   <el-tag size="small" type="danger">{{ strategy.type }}</el-tag> 
                 </div>
                 <p class="strategy-description">{{ strategy.description || '暂无描述' }}</p>
                 <div class="strategy-actions">
                   <el-button type="primary" size="small" @click="navigateToDetail(strategy.id)">查看详情</el-button>
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
            <el-row :gutter="20" type="flex" style="flex-wrap: wrap;">
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
        <el-row :gutter="20" type="flex" style="flex-wrap: wrap;">
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
        <el-row :gutter="20" type="flex" style="flex-wrap: wrap;">
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
              <el-button size="mini" type="text" @click="handleView(scope.row)">查看</el-button> <!-- Keep View button -->
              <el-button size="mini" type="text" @click="handleBacktest(scope.row)">回测</el-button> <!-- This now triggers the new dialog -->
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

    <!-- 策略详情对话框 (View Dialog) - REMOVE Backtest Tab -->
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
                <!-- Removed Backtest button from here -->
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- Backtest标签页 - ENTIRELY REMOVED -->
        <!-- <el-tab-pane label="回测" name="backtest"> ... </el-tab-pane> -->

        <!-- 参数优化标签页 (Keep Optimize Tab for now) -->
        <el-tab-pane label="参数优化" name="optimize">
         <!-- ... (existing content for optimize tab) ... -->
        </el-tab-pane>

        <!-- 实盘交易标签页 (Keep Live Tab for now) -->
        <el-tab-pane label="实盘交易" name="live">
          <!-- ... (existing content for live tab) ... -->
        </el-tab-pane>
      </el-tabs>
       <span slot="footer" class="dialog-footer">
         <el-button @click="strategyDetailVisible = false">关闭</el-button>
      </span>
    </el-dialog>

    <!-- 新的回测配置对话框 (New Backtest Dialog) -->
    <!-- Removed the new backtest dialog -->

  </div>
</template>

<script>
// 导入 API 函数 - 需要添加 runStrategyBacktest
import { getStrategies, getUserStrategies, getStrategyTypes, runStrategyBacktest } from '@/api/strategies'; 
import { getAvailableSymbols, getAvailableExchanges, getAvailableIntervals, getBarData } from '@/api/data';
import dayjs from 'dayjs'; // 引入 dayjs 用于日期处理

export default {
  name: 'StrategyCenterView',
  data() {
    // 设置默认回测日期
    const endDate = dayjs().format('YYYY-MM-DD');
    const startDate = dayjs().subtract(3, 'month').format('YYYY-MM-DD');

    return {
      // --- Restore missing data properties for general view ---
      strategiesLoading: false,
      allStrategies: [], // All strategies fetched
      basicStrategies: [], // Filtered basic strategies (non-AI)
      advancedStrategies: [], // Filtered advanced strategies (AI)
      filteredBasicStrategies: [], // Basic strategies currently displayed after filtering
      strategyTypes: [], 
      selectedBasicType: 'all', 
      activeTab: 'basic-strategies', // Default active tab
      myStrategiesLoading: false,
      myStrategiesList: [], 
      currentUserId: 1, 
      componentActiveTab: 'factor-library', // For component library sub-tabs
      builderMode: 'visual', // For builder tab
      // --- Restore missing data properties for builder tab ---
      strategyType: 'cta', // Default value for the radio group in builder
      indicators: [],     // Default value for the checkbox group in builder
      strategyName: '',    // Default value for the strategy name input in builder
      maPeriod: 20,       // Default value for MA period input in builder
      rsiPeriod: 14,      // Default value for RSI period input in builder
      positionSize: 10,   // Default value for position size slider in builder
      // --- Keep data for Strategy Detail Dialog (View Dialog) ---
      strategyDetailVisible: false,
      currentStrategy: null, 
      detailActiveTab: 'info', 
      strategyParams: {}, 
      // --- Removed data for the NEW Backtest Dialog ---
    };
  },
  computed: {
      // --- Restore missing computed property ---
      basicStrategyTypes() {
          // Ensure strategyTypes is always an array before filtering
          // Use 'basic' types from allStrategies instead of the separate API call result
          const types = new Set(this.basicStrategies.map(s => s.name)); // Assuming type comes from name for basic dropdown filter?
          return Array.from(types);
      }
      // --- (Other computed properties if any) ---
  },
  created() {
    this.fetchAllStrategiesAndGroup();
    this.fetchMyStrategies(); 
    this.fetchStrategyTypes();
  },
  methods: {
    // --- Restore missing methods ---
    handleTabClick(tab) {
        console.log("Tab clicked:", tab.name);
    },
    filterBasicStrategies() {
        if (this.selectedBasicType === 'all') {
            this.filteredBasicStrategies = [...this.basicStrategies]; // Create a copy
        } else {
            this.filteredBasicStrategies = this.basicStrategies.filter(s => s.type === this.selectedBasicType);
        }
         console.log("Filtered Basic Strategies:", this.filteredBasicStrategies);
    },
    // --- Keep existing methods ---
    fetchAllStrategiesAndGroup() {
      this.strategiesLoading = true;
      getStrategies()
        .then(response => {
          if (response.data && response.data.success) {
            this.allStrategies = response.data.data || [];
            this.groupStrategies(); 
            this.filterBasicStrategies(); // Initial filter after grouping
          } else {
            this.$message.error(response.data.message || '加载策略列表失败');
            this.allStrategies = [];
            this.basicStrategies = [];
            this.advancedStrategies = [];
            this.filteredBasicStrategies = []; // Ensure reset on error
          }
        })
        .catch(error => {
          console.error('加载策略列表错误:', error);
          this.$message.error('网络错误，无法加载策略列表');
           this.allStrategies = [];
           this.basicStrategies = [];
           this.advancedStrategies = [];
           this.filteredBasicStrategies = []; // Ensure reset on error
        })
        .finally(() => {
          this.strategiesLoading = false;
        });
    },
    groupStrategies() {
        this.basicStrategies = this.allStrategies.filter(s => s.type === 'basic'); // Changed from !== 'AI策略'
        this.advancedStrategies = this.allStrategies.filter(s => s.type === 'advanced'); // Changed from === 'AI策略'
        console.log("Basic Strategies:", this.basicStrategies);
        console.log("Advanced Strategies:", this.advancedStrategies);
    },
    fetchStrategyTypes() {
      getStrategyTypes()
        .then(response => {
          if (response.data && response.data.success) {
            // Ensure strategyTypes is always an array
            this.strategyTypes = Array.isArray(response.data.data) ? response.data.data : [];
          } else {
            this.$message.error(response.data.message || '加载策略类型失败');
            this.strategyTypes = []; // Reset on error
          }
        })
        .catch(error => {
          console.error('加载策略类型错误:', error);
          this.$message.error('网络错误，无法加载策略类型');
           this.strategyTypes = []; // Reset on error
        });
    },
    fetchMyStrategies() {
      // ... (fetchMyStrategies logic remains the same) ...
       this.myStrategiesLoading = true;
      getUserStrategies(this.currentUserId)
        .then(response => {
          if (response.data && response.data.success) {
            this.myStrategiesList = response.data.data || [];
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
    navigateToDetail(strategyId) {
      // ... (navigateToDetail logic remains the same) ...
        const idToUse = typeof strategyId === 'object' ? strategyId.id : strategyId;
        this.$router.push(`/strategy/${idToUse}`);
    },
    handleView(row) {
      // ... (handleView logic remains the same) ...
        this.currentStrategy = JSON.parse(JSON.stringify(row)); 
        this.strategyParams = this.currentStrategy.parameters || {}; 
        this.strategyDetailVisible = true;
        this.detailActiveTab = 'info'; 
        this.optimizeResult.hasResult = false; 
    },
    handleBacktest(row) {
      console.log("Navigating to backtest page for strategy:", row.name, "ID:", row.id);
      this.$router.push({ name: 'BacktestPageWithStrategy', params: { strategyId: row.id } });
    },
    handleOptimize(row) {
      // ... (handleOptimize logic remains the same) ...
        this.handleView(row); 
        this.detailActiveTab = 'optimize';
    },
    handleAction(row) {
      // ... (handleAction logic remains the same) ...
       if (row.status === '运行中') {
        this.$confirm('确定要停止该策略吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          row.status = '待运行'; // TODO: Call stop API
          this.$message({
            type: 'success',
            message: `策略 ${row.name} 已停止`
          });
          this.fetchMyStrategies(); 
        }).catch(() => {});
      } else {
         this.$message({
            type: 'info',
            message: `正在启动策略 ${row.name}...`
          });
         setTimeout(() => {
            row.status = '运行中'; // TODO: Call start API
            this.$message.success(`策略 ${row.name} 已启动`);
            this.fetchMyStrategies(); 
         }, 1000);
      }
    },
    saveStrategyParams() {
      // ... (saveStrategyParams logic remains the same) ...
       this.$message({
        type: 'success',
        message: '策略参数保存成功 (模拟)' 
      });
    },
  }
}
</script>

<style>
/* ... (existing global styles) ... */

/* Styles for result display in backtest dialog */
.result-title {
  margin: 0 0 10px;
  font-size: 14px;
  color: #606266;
  font-weight: normal;
}
.result-value {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}
.result-value.positive {
  color: #67C23A;
}
.result-value.negative {
  color: #F56C6C;
}
</style>

<style scoped>
/* Make cards have consistent height and use flex layout */
.strategy-card {
  height: 100%; /* Ensure card takes full height of the column */
  display: flex;
  flex-direction: column;
}

/* Allow card content to grow and push actions down */
.strategy-card-content {
  flex-grow: 1; /* Allow content to take available space */
  display: flex;
  flex-direction: column;
  height: 100%; /* Ensure content fills the card */
}

.strategy-card-header {
  display: flex;
  justify-content: space-between; /* Space between title and tags */
  align-items: flex-start; /* Align items to the top */
  margin-bottom: 10px;
}

.strategy-title {
  margin: 0;
  font-size: 1.1em; 
  font-weight: 600;
  margin-right: 10px; /* Add some space between title and tag */
  /* Optional: Allow title to wrap if too long */
  white-space: normal; 
  overflow-wrap: break-word;
}

.strategy-description {
  flex-grow: 1; /* Allow description to take up most space */
  font-size: 0.9em;
  color: #606266;
  line-height: 1.4;
  margin-bottom: 15px;
  /* Optional: Limit description lines and add ellipsis */
  /* display: -webkit-box;
  -webkit-line-clamp: 3; 
  -webkit-box-orient: vertical;  
  overflow: hidden;
  text-overflow: ellipsis; */
}

/* Push actions to the bottom */
.strategy-actions {
  margin-top: auto; /* Push to the bottom */
  text-align: left; /* Align button to the left */
}

/* General metrics styling (if needed later) */
.strategy-metrics {
  margin-bottom: 10px;
}

.metric {
  font-size: 0.85em;
  color: #909399;
  margin-right: 15px;
}

.metric-value {
  font-weight: 600;
  color: #303133;
}

.metric-value.positive {
  color: #67C23A;
}

.metric-value.negative {
  color: #F56C6C;
}

/* Style for component library tabs */
.component-tabs {
    margin-top: 20px;
}

/* Adjust table status tag colors if needed */
/* .el-tag--success { background-color: #f0f9eb; border-color: #e1f3d8; color: #67c23a; } */
/* .el-tag--warning { background-color: #fdf6ec; border-color: #faecd8; color: #e6a23c; } */
/* .el-tag--info { background-color: #f4f4f5; border-color: #e9e9eb; color: #909399; } */
/* .el-tag--danger { background-color: #fef0f0; border-color: #fde2e2; color: #f56c6c; } */
</style>
