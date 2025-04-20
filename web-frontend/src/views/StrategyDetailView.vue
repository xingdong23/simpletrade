<template>
  <div class="strategy-detail-container">
    <div class="page-header">
      <el-page-header @back="goBack" :content="'策略详情: ' + (strategy ? strategy.name : '')"></el-page-header>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="策略信息" name="info">
          <!-- 策略基本信息 -->
          <el-descriptions :column="2" border>
            <el-descriptions-item label="策略名称">{{ strategy ? strategy.name : '' }}</el-descriptions-item>
            <el-descriptions-item label="策略类型">{{ strategy ? strategy.type : '' }}</el-descriptions-item>
            <el-descriptions-item label="标识符">{{ strategy ? strategy.identifier : '' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ strategy ? strategy.createTime : '' }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="strategy && strategy.status === '运行中' ? 'success' : strategy && strategy.status === '待运行' ? 'warning' : 'info'" size="small">
                {{ strategy ? strategy.status : '' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="复杂度">
              <el-rate v-model="strategyComplexity" disabled text-color="#ff9900" score-template="{value}"></el-rate>
            </el-descriptions-item>
            <el-descriptions-item label="资源需求">
              <el-tag size="small" type="success">运行速度: 快</el-tag>
              <el-tag size="small" type="success" style="margin-left: 10px;">计算资源: 低</el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <!-- 策略参数 -->
          <div style="margin-top: 20px;">
            <h3>策略参数 (默认)</h3>
            <!-- TODO: Dynamically generate based on strategy.parameters -->
            <el-form label-width="150px" style="margin-top: 20px;">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="短周期移动平均线">
                    <el-input-number v-model="strategyParams.fast_window" disabled></el-input-number>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="长周期移动平均线">
                    <el-input-number v-model="strategyParams.long_window" disabled></el-input-number>
                  </el-form-item>
                </el-col>
              </el-row>
              <!-- Add other default params as needed -->
            </el-form>
          </div>

          <!-- 显示策略代码 -->
          <div v-if="strategy && strategy.code" style="margin-top: 20px;">
            <h3>策略代码</h3>
            <el-card shadow="never" style="max-height: 400px; overflow-y: auto;">
              <pre style="margin: 0;"><code class="language-python">{{ strategy.code }}</code></pre>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="回测" name="backtest" v-loading="backtestLoading">
          <el-form :inline="false" label-width="120px" class="demo-form-inline" style="margin-bottom: 20px;">
            <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="合约代码">
                        <el-input v-model="backtestSymbol" placeholder="例如 rb2410"></el-input>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                     <el-form-item label="交易所">
                        <el-input v-model="backtestExchange" placeholder="例如 SHFE"></el-input>
                    </el-form-item>
                </el-col>
            </el-row>
            <el-row :gutter="20">
                 <el-col :span="12">
                    <el-form-item label="K线周期">
                        <el-select v-model="backtestInterval" placeholder="选择周期">
                            <el-option label="1分钟" value="1m"></el-option>
                            <el-option label="5分钟" value="5m"></el-option>
                            <el-option label="15分钟" value="15m"></el-option>
                            <el-option label="30分钟" value="30m"></el-option>
                            <el-option label="1小时" value="1h"></el-option>
                            <el-option label="4小时" value="4h"></el-option>
                            <el-option label="日线" value="d"></el-option>
                            <el-option label="周线" value="w"></el-option>
                        </el-select>
                    </el-form-item>
                 </el-col>
                 <el-col :span="12">
                    <el-form-item label="初始资金">
                        <el-input-number v-model="backtestParams.initialCapital" :min="1000" :step="10000"></el-input-number>
                    </el-form-item>
                 </el-col>
            </el-row>
             <el-row :gutter="20">
                <el-col :span="12">
                     <el-form-item label="起始日期">
                        <el-date-picker v-model="backtestParams.startDate" type="date" placeholder="选择日期" value-format="yyyy-MM-dd"></el-date-picker>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="结束日期">
                        <el-date-picker v-model="backtestParams.endDate" type="date" placeholder="选择日期" value-format="yyyy-MM-dd"></el-date-picker>
                    </el-form-item>
                </el-col>
            </el-row>
            <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="手续费率">
                         <el-input-number v-model="backtestRate" :precision="5" :step="0.0001" :min="0"></el-input-number>
                    </el-form-item>
                </el-col>
                 <el-col :span="12">
                    <el-form-item label="滑点">
                        <el-input-number v-model="backtestSlippage" :precision="2" :step="0.1" :min="0"></el-input-number>
                    </el-form-item>
                 </el-col>
            </el-row>
             <el-row>
                <el-col :span="24">
                    <el-form-item label="自定义参数(JSON)">
                        <el-input type="textarea" v-model="backtestUserParamsJson" placeholder='可选, 输入JSON覆盖默认参数, 例如: {"fast_window": 5, "slow_window": 15}'></el-input>
                    </el-form-item>
                </el-col>
            </el-row>
            <el-form item>
              <el-button type="primary" @click="runBacktest">运行回测</el-button>
            </el-form>
          </el-form>

          <!-- 回测结果 -->
          <div v-if="backtestResult.hasResult">
            <el-divider content-position="left">回测结果 (记录 ID: {{ backtestResult.record_id }})</el-divider>
            <!-- 回测指标 -->
            <el-row :gutter="20" style="margin-bottom: 20px;">
              <el-col :span="6">
                <el-card shadow="hover">
                  <div style="text-align: center;">
                    <h3 class="result-title">总收益率</h3>
                    <p class="result-value positive">{{ formatPercent(backtestResult.statistics.total_return) }}</p>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <div style="text-align: center;">
                    <h3 class="result-title">年化收益率</h3>
                    <p class="result-value positive">{{ formatPercent(backtestResult.statistics.annual_return) }}</p>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <div style="text-align: center;">
                    <h3 class="result-title">最大回撤率</h3>
                    <p class="result-value negative">{{ formatPercent(backtestResult.statistics.max_drawdown) }}</p>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <div style="text-align: center;">
                    <h3 class="result-title">胜率</h3>
                    <p class="result-value">{{ formatPercent(backtestResult.statistics.win_rate) }}</p>
                  </div>
                </el-card>
              </el-col>
              <!-- Add more statistic cards as needed -->
               <el-col :span="6" style="margin-top: 20px;">
                <el-card shadow="hover">
                  <div style="text-align: center;">
                    <h3 class="result-title">夏普比率</h3>
                    <p class="result-value">{{ formatNumber(backtestResult.statistics.sharpe_ratio, 2) }}</p>
                  </div>
                </el-card>
              </el-col>
               <el-col :span="6" style="margin-top: 20px;">
                <el-card shadow="hover">
                  <div style="text-align: center;">
                    <h3 class="result-title">盈亏比</h3>
                    <p class="result-value">{{ formatNumber(backtestResult.statistics.profit_factor, 2) }}</p>
                  </div>
                </el-card>
              </el-col>
               <el-col :span="6" style="margin-top: 20px;">
                <el-card shadow="hover">
                  <div style="text-align: center;">
                    <h3 class="result-title">交易次数</h3>
                    <p class="result-value">{{ backtestResult.statistics.total_trade_count }}</p>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 收益曲线图 (Placeholder) -->
            <!-- ... existing placeholder ... -->

            <!-- 交易记录 (Placeholder/Optional) -->
            <!-- ... existing placeholder or table for trades if API returns them ... -->

            <!-- 部署到实盘按钮 (保留) -->
            <!-- ... existing button ... -->
          </div>
          <div v-else style="text-align: center; padding: 50px 0;">
            <i class="el-icon-data-analysis" style="font-size: 48px; color: #909399; margin-bottom: 20px;"></i>
            <p>请配置参数并点击"运行回测"按钮开始回测。</p>
          </div>
        </el-tab-pane>
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

            <!-- 参数组合列表 -->
            <el-card shadow="hover">
              <div slot="header">
                <span>参数组合列表</span>
              </div>
              <el-table :data="optimizeResult.paramSets" style="width: 100%">
                <el-table-column v-for="(value, key) in optimizeResult.bestParams" :key="key" :prop="key" :label="key" width="120"></el-table-column>
                <el-table-column prop="totalReturn" label="总收益率" width="120">
                  <template slot-scope="scope">
                    <span>{{ scope.row.totalReturn }}%</span>
                  </template>
                </el-table-column>
                <el-table-column prop="maxDrawdown" label="最大回撤" width="120">
                  <template slot-scope="scope">
                    <span>{{ scope.row.maxDrawdown }}%</span>
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
        <el-tab-pane label="实盘交易" name="live">
          <div v-if="strategy && strategy.status === '运行中'">
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
                    <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">交易笔数</h3>
                    <p style="font-size: 18px; font-weight: 600; color: #303133; margin: 0;">12</p>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div style="text-align: center;">
                    <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">胜率</h3>
                    <p style="font-size: 18px; font-weight: 600; color: #409EFF; margin: 0;">58%</p>
                  </div>
                </el-col>
              </el-row>
            </el-card>

            <!-- 当前持仓 -->
            <el-card shadow="hover" style="margin-bottom: 20px;">
              <div slot="header">
                <span>当前持仓</span>
              </div>
              <el-table :data="[{symbol: 'AAPL', name: '苹果公司', quantity: 100, price: 175.25, marketValue: 17525, profit: 525, profitRatio: 3.1}]" style="width: 100%">
                <el-table-column prop="symbol" label="代码" width="120"></el-table-column>
                <el-table-column prop="name" label="名称" width="180"></el-table-column>
                <el-table-column prop="quantity" label="数量" width="100"></el-table-column>
                <el-table-column prop="price" label="当前价" width="120"></el-table-column>
                <el-table-column prop="marketValue" label="市值" width="120"></el-table-column>
                <el-table-column prop="profit" label="盈亏" width="120">
                  <template slot-scope="scope">
                    <span :style="{ color: scope.row.profit >= 0 ? '#67C23A' : '#F56C6C' }">
                      {{ scope.row.profit >= 0 ? '+' : '' }}{{ scope.row.profit }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="profitRatio" label="盈亏比例" width="120">
                  <template slot-scope="scope">
                    <span :style="{ color: scope.row.profitRatio >= 0 ? '#67C23A' : '#F56C6C' }">
                      {{ scope.row.profitRatio >= 0 ? '+' : '' }}{{ scope.row.profitRatio }}%
                    </span>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>

            <!-- 交易记录 -->
            <el-card shadow="hover">
              <div slot="header">
                <span>交易记录</span>
              </div>
              <el-table :data="liveTradeRecords" style="width: 100%">
                <el-table-column prop="date" label="时间" width="180"></el-table-column>
                <el-table-column prop="type" label="类型" width="100">
                  <template slot-scope="scope">
                    <el-tag :type="scope.row.type === '买入' ? 'success' : 'danger'" size="small">{{ scope.row.type }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="price" label="价格" width="120"></el-table-column>
                <el-table-column prop="quantity" label="数量" width="120"></el-table-column>
                <el-table-column prop="amount" label="金额" width="120"></el-table-column>
                <el-table-column prop="status" label="状态" width="120">
                  <template slot-scope="scope">
                    <el-tag :type="scope.row.status === '已成交' ? 'success' : scope.row.status === '已取消' ? 'info' : 'warning'" size="small">{{ scope.row.status }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>

            <!-- 停止策略按钮 -->
            <div style="margin-top: 20px; text-align: center;">
              <el-button type="danger" @click="stopStrategy">停止策略</el-button>
            </div>
          </div>
          <div v-else style="text-align: center; padding: 50px 0;">
            <i class="el-icon-warning-outline" style="font-size: 48px; color: #E6A23C; margin-bottom: 20px;"></i>
            <p>策略当前未在实盘运行。请先运行回测，然后部署到实盘。</p>
            <el-button type="primary" @click="activeTab = 'backtest'">运行回测</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import { getStrategyDetail, runStrategyBacktest } from '@/api/strategies';
import dayjs from 'dayjs';

export default {
  name: 'StrategyDetailView',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    const endDate = dayjs().format('YYYY-MM-DD');
    const startDate = dayjs().subtract(3, 'month').format('YYYY-MM-DD');
    
    return {
      strategy: null,
      activeTab: 'info',
      strategyComplexity: 3,
      strategyParams: {},
      loading: false,
      error: null,
      
      backtestLoading: false,
      backtestSymbol: '',
      backtestExchange: '',
      backtestInterval: 'd',
      backtestRate: 0.0001,
      backtestSlippage: 0.2,
      backtestUserParamsJson: '',
      backtestParams: {
        startDate: startDate,
        endDate: endDate,
        initialCapital: 100000
      },
      backtestResult: {
        hasResult: false,
        record_id: null,
        statistics: {}
      },
      optimizeParams: {
        target: 'totalReturn',
        parameters: []
      },
      optimizeResult: {
        hasResult: false,
        bestParams: {},
        paramSets: []
      },
      liveTradeRecords: []
    };
  },
  computed: {
    parameterList() {
      if (!this.strategy || !this.strategy.parameters || typeof this.strategy.parameters !== 'object') {
        return [];
      }
      return Object.entries(this.strategy.parameters).map(([name, details]) => ({
        name,
        ...details
      }));
    }
  },
  methods: {
    goBack() {
      this.$router.push('/strategy-center');
    },
    async fetchStrategyDetail() {
      console.log('StrategyDetailView: fetchStrategyDetail() called with id:', this.id);
      this.loading = true;
      this.error = null;
      try {
        const response = await getStrategyDetail(this.id);
        if (response.data && response.data.success) {
          this.strategy = response.data.data;
          this.strategyComplexity = this.strategy.complexity || 3;
          this.strategyParams = this.strategy.parameters || {};
        } else {
          this.error = response.data.message || '获取策略详情失败';
          this.strategy = null;
        }
      } catch (err) {
        console.error('Error fetching strategy detail:', err);
        this.error = (err.response && err.response.data && err.response.data.message) || err.message || '网络错误或服务器内部错误';
        this.strategy = null;
      } finally {
        this.loading = false;
      }
    },
    async runBacktest() {
      if (!this.strategy) {
        this.$message.error('策略信息未加载，无法回测');
        return;
      }
      if (!this.backtestSymbol || !this.backtestExchange) {
          this.$message.error('请输入合约代码和交易所');
          return;
      }
      if (!this.backtestParams.startDate || !this.backtestParams.endDate) {
          this.$message.error('请选择回测起始和结束日期');
          return;
      }
      if (dayjs(this.backtestParams.endDate).isBefore(dayjs(this.backtestParams.startDate))) {
           this.$message.error('结束日期不能早于起始日期');
          return;
      }

      let userParams = null;
      if (this.backtestUserParamsJson.trim()) {
        try {
          userParams = JSON.parse(this.backtestUserParamsJson);
          if (typeof userParams !== 'object' || userParams === null) {
             throw new Error('自定义参数必须是 JSON 对象');
          }
        } catch (e) {
          this.$message.error(`自定义参数 JSON 格式错误: ${e.message}`);
          return;
        }
      }

      const backtestConfig = {
        strategy_id: parseInt(this.id),
        symbol: this.backtestSymbol,
        exchange: this.backtestExchange,
        interval: this.backtestInterval,
        start_date: this.backtestParams.startDate,
        end_date: this.backtestParams.endDate,
        initial_capital: this.backtestParams.initialCapital,
        rate: this.backtestRate,
        slippage: this.backtestSlippage,
        parameters: userParams,
        user_id: 1
      };

      this.backtestLoading = true;
      this.backtestResult.hasResult = false;
      try {
        console.log("Sending backtest request:", backtestConfig);
        const response = await runStrategyBacktest(backtestConfig);
        console.log("Backtest response:", response);

        if (response.data && response.data.success) {
          this.$message.success('回测成功');
          this.backtestResult.hasResult = true;
          this.backtestResult.record_id = response.data.data.record_id;
          this.backtestResult.statistics = response.data.data.statistics || {};
        } else {
          this.$message.error(`回测失败: ${response.data.message || '未知错误'}`);
          this.backtestResult.statistics = {};
        }
      } catch (err) {
        console.error('Error running backtest:', err);
        const errorMsg = (err.response && err.response.data && err.response.data.message)
                           || (err.response && err.response.data && err.response.detail)
                           || err.message
                           || '网络错误或服务器内部错误';
        this.$message.error(`回测请求失败: ${errorMsg}`);
         this.backtestResult.statistics = {};
      } finally {
        this.backtestLoading = false;
      }
    },
    formatPercent(value) {
        if (value === null || value === undefined || isNaN(value)) return '-';
        return (value * 100).toFixed(2) + '%';
    },
    formatNumber(value, precision = 2) {
        if (value === null || value === undefined || isNaN(value)) return '-';
        return Number(value).toFixed(precision);
    },
    saveStrategyParams() {
      this.$message({
        type: 'success',
        message: '策略参数保存成功'
      });
    },
    deployToLive() {
      this.$confirm('确定要将策略部署到实盘吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$message({
          type: 'info',
          message: '正在部署策略...'
        });

        setTimeout(() => {
          if (this.strategy) {
            this.strategy.status = '运行中';
            this.activeTab = 'live';
            this.liveTradeRecords = [
              { date: '2023-10-25 09:30:15', type: '买入', price: '156.50', quantity: '100', amount: '15,650.00', status: '已成交' },
              { date: '2023-10-25 10:15:30', type: '卖出', price: '157.25', quantity: '50', amount: '7,862.50', status: '已成交' },
              { date: '2023-10-25 14:20:45', type: '买入', price: '155.75', quantity: '50', amount: '7,787.50', status: '已成交' }
            ];

            this.$message({
              type: 'success',
              message: `策略 ${this.strategy.name} 已成功部署到实盘`
            });
          }
        }, 1500);
      }).catch(() => {});
    },
    runOptimization() {
      if (!this.optimizeParams.parameters.length) {
        this.$message({
          type: 'warning',
          message: '请选择要优化的参数'
        });
        return;
      }

      this.$message({
        type: 'info',
        message: '正在运行参数优化...'
      });

      setTimeout(() => {
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
    applyOptimizedParams() {
      Object.assign(this.strategyParams, this.optimizeResult.bestParams);
      this.activeTab = 'info';
      this.$message({
        type: 'success',
        message: '已应用最佳参数'
      });
    },
    applyParamSet(paramSet) {
      Object.keys(paramSet).forEach(key => {
        if (key !== 'totalReturn' && key !== 'maxDrawdown' && key !== 'winRate') {
          this.strategyParams[key] = paramSet[key];
        }
      });
      this.activeTab = 'info';
      this.$message({
        type: 'success',
        message: '已应用选中的参数组合'
      });
    },
    stopStrategy() {
      this.$confirm('确定要停止该策略吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        if (this.strategy) {
          this.strategy.status = '待运行';
          this.$message({
            type: 'success',
            message: `策略 ${this.strategy.name} 已停止`
          });
        }
      }).catch(() => {});
    }
  },
  created() {
    console.log('StrategyDetailView: Component created with id prop:', this.id);
    this.fetchStrategyDetail();
  },
  watch: {
    id(newId, oldId) {
      console.log(`StrategyDetailView: Watcher triggered. ID changed from ${oldId} to ${newId}`);
      if (newId && newId !== oldId) {
        this.fetchStrategyDetail();
        this.backtestResult.hasResult = false;
        this.backtestResult.statistics = {};
        this.backtestSymbol = '';
        this.backtestExchange = '';
        this.backtestUserParamsJson = '';
      }
    }
  }
};
</script>

<style scoped>
.strategy-detail-container {
  padding: 20px;
}
.page-header {
  margin-bottom: 20px;
}
.main-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
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
