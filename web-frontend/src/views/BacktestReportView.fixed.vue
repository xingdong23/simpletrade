<template>
  <div class="backtest-report-view">
    <el-card v-loading="loading" class="box-card">
      <div v-if="error" class="error-message">
        <el-alert
          :title="'获取回测报告失败: ' + (error.message || error)"
          type="error"
          show-icon
          :closable="false">
          <el-button type="text" @click="fetchBacktestReport">重试</el-button>
        </el-alert>
      </div>

      <div v-if="!loading && backtestReport">
        <el-card class="inner-card">
          <div slot="header" class="clearfix">
            <span class="report-title">回测报告: {{ backtestReport.backtest_id }}</span>
            <div class="report-subtitle">执行于: {{ formatDateTime(backtestReport.ran_at) }}</div>
          </div>
        </el-card>

        <!-- 配置信息 -->
        <el-card class="inner-card">
          <div slot="header" class="clearfix">
            <span>回测配置</span>
          </div>
          <el-descriptions border>
            <el-descriptions-item v-for="(value, key) in backtestReport.config" :key="key" :label="formatConfigKey(key)">
              <span v-if="typeof value === 'object'">{{ JSON.stringify(value, null, 2) }}</span>
              <span v-else>{{ value }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 统计摘要 -->
        <el-card class="inner-card">
          <div slot="header" class="clearfix">
            <span>统计摘要</span>
          </div>
          <el-descriptions border>
            <el-descriptions-item v-for="(value, key) in backtestReport.summary_stats" :key="key" :label="formatSummaryStatKey(key)">
              <span>{{ formatSummaryStatValue(value, key) }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 资金曲线图 -->
        <el-card class="inner-card">
          <div slot="header" class="clearfix">
            <span>资金曲线</span>
          </div>
          <EquityChart :equity-curve="backtestReport.equity_curve" />
          <div v-if="!backtestReport.equity_curve || backtestReport.equity_curve.length === 0" class="no-data-message">
            资金曲线数据不可用。
          </div>
        </el-card>

        <!-- 交易列表 -->
        <el-card class="inner-card">
          <div slot="header" class="clearfix">
            <span>交易详情</span>
          </div>
          <el-table
            :data="backtestReport.trades"
            border
            style="width: 100%"
            :default-sort="{prop: 'datetime', order: 'ascending'}"
          >
            <el-table-column
              prop="datetime"
              label="时间"
              sortable
              :formatter="(row) => formatDateTime(row.datetime)"
            ></el-table-column>
            <el-table-column
              prop="symbol"
              label="标的"
              sortable
            ></el-table-column>
            <el-table-column
              prop="exchange"
              label="交易所"
              sortable
            ></el-table-column>
            <el-table-column
              prop="direction"
              label="方向"
              sortable
              align="center"
            ></el-table-column>
            <el-table-column
              prop="offset"
              label="开平"
              sortable
              align="center"
            ></el-table-column>
            <el-table-column
              prop="price"
              label="价格"
              sortable
              align="right"
              :formatter="(row) => row.price.toFixed(2)"
            ></el-table-column>
            <el-table-column
              prop="volume"
              label="数量"
              sortable
              align="right"
              :formatter="(row) => row.volume.toFixed(0)"
            ></el-table-column>
            <el-table-column
              prop="pnl"
              label="盈亏"
              sortable
              align="right"
            >
              <template slot-scope="scope">
                <span :class="scope.row.pnl > 0 ? 'text-positive' : (scope.row.pnl < 0 ? 'text-negative' : '')">
                  {{ scope.row.pnl !== null && scope.row.pnl !== undefined ? scope.row.pnl.toFixed(2) : 'N/A' }}
                </span>
              </template>
            </el-table-column>
          </el-table>
          <p v-if="!backtestReport.trades || backtestReport.trades.length === 0">暂无交易数据。</p>
        </el-card>
      </div>
      <div v-else-if="!loading && !error">
        <p>没有获取到回测报告数据。</p>
      </div>
    </el-card>
  </div>
</template>

<script>
import { getBacktestReport } from '@/api/backtests';
import EquityChart from '@/components/EquityChart.vue';

export default {
  name: 'BacktestReportView',
  components: {
    EquityChart
  },
  props: {
    backtest_id: {
      type: [String, Number],
      default: null
    }
  },
  data() {
    return {
      backtestReport: null,
      loading: true,
      error: null,
      configKeyMap: {
        strategy_id: '策略ID',
        strategy_name: '策略名称',
        class_name: '策略类名',
        symbol: '交易标的',
        exchange: '交易所',
        interval: '时间周期',
        start_date: '开始日期',
        end_date: '结束日期',
        capital: '初始资金',
        rate: '手续费率',
        slippage: '滑点',
        mode: '回测模式',
        parameters: '策略参数'
      },
      summaryStatKeyMap: {
        total_days: "总交易日",
        profit_days: "盈利交易日",
        loss_days: "亏损交易日",
        end_balance: "期末权益",
        max_drawdown: "最大回撤",
        max_drawdown_percent: "最大回撤率",
        max_drawdown_start: "最大回撤开始日期",
        max_drawdown_end: "最大回撤结束日期",
        total_net_pnl: "总盈亏",
        total_commission: "总手续费",
        total_slippage: "总滑点",
        total_turnover: "总成交额",
        total_trade_count: "总成交次数",
        long_trade_count: "多头交易次数",
        short_trade_count: "空头交易次数",
        win_trade_count: "盈利次数",
        loss_trade_count: "亏损次数",
        win_rate: "胜率",
        average_win_pnl: "平均盈利",
        average_loss_pnl: "平均亏损",
        profit_loss_ratio: "盈亏比",
        sharpe_ratio: "夏普比率",
        sortino_ratio: "索提诺比率",
        calmar_ratio: "卡玛比率",
        annual_return: "年化收益率"
      }
    };
  },
  computed: {
    backtestIdValue() {
      return this.backtest_id || (this.$route && this.$route.params && this.$route.params.backtest_id);
    }
  },
  methods: {
    formatConfigKey(key) {
      return this.configKeyMap[key] || key;
    },
    formatSummaryStatKey(key) {
      return this.summaryStatKeyMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },
    formatSummaryStatValue(value, key) {
      if (typeof value === 'number') {
        if (key.includes('rate') || key.includes('percent') || key === 'win_rate') {
          return (value * 100).toFixed(2) + '%';
        }
        return value.toFixed(2);
      }
      if (key.includes('date') && value && typeof value === 'string') {
        return this.formatDateTime(value, 'YYYY-MM-DD');
      }
      return value;
    },
    formatDateTime(dateTimeString, formatStr = 'YYYY-MM-DD HH:mm:ss') {
      if (!dateTimeString) return '';
      const date = new Date(dateTimeString);
      if (formatStr === 'YYYY-MM-DD') {
        return date.toISOString().split('T')[0];
      }
      return date.toLocaleString();
    },
    async fetchBacktestReport() {
      if (!this.backtestIdValue) {
        this.error = '未提供回测ID';
        this.loading = false;
        return;
      }
      this.loading = true;
      this.error = null;
      try {
        const response = await getBacktestReport(this.backtestIdValue);
        this.backtestReport = response;
      } catch (err) {
        console.error('获取回测报告失败:', err);
        this.error = err.message || '发生未知错误';
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchBacktestReport();
  }
};
</script>

<style scoped>
.backtest-report-view {
  max-width: 1200px;
  margin: auto;
  padding: 20px;
}
.inner-card {
  margin-bottom: 20px;
}
.report-title {
  font-size: 18px;
  font-weight: bold;
}
.report-subtitle {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
.text-positive {
  color: #67C23A;
}
.text-negative {
  color: #F56C6C;
}
.no-data-message {
  text-align: center;
  color: #909399;
  padding: 20px;
}
.error-message {
  margin-bottom: 20px;
}
</style>
