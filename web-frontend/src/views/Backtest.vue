<template>
  <div class="backtest-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>策略回测</span>
      </div>
      
      <el-form :model="backtestForm" label-width="100px" :rules="rules" ref="backtestForm">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="策略名称" prop="strategyName">
              <el-input v-model="backtestForm.strategyName" placeholder="请输入策略名称"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="策略类型" prop="strategyType">
              <el-select v-model="backtestForm.strategyType" placeholder="请选择策略类型">
                <el-option label="CTA策略" value="cta"></el-option>
                <el-option label="选股策略" value="stock"></el-option>
                <el-option label="套利策略" value="arbitrage"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="交易品种" prop="symbol">
              <el-select v-model="backtestForm.symbol" placeholder="请选择交易品种" filterable>
                <el-option
                  v-for="item in symbolOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="K线周期" prop="interval">
              <el-select v-model="backtestForm.interval" placeholder="请选择K线周期">
                <el-option label="1分钟" value="1m"></el-option>
                <el-option label="5分钟" value="5m"></el-option>
                <el-option label="15分钟" value="15m"></el-option>
                <el-option label="30分钟" value="30m"></el-option>
                <el-option label="1小时" value="1h"></el-option>
                <el-option label="日线" value="1d"></el-option>
                <el-option label="周线" value="1w"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="startDate">
              <el-date-picker
                v-model="backtestForm.startDate"
                type="date"
                placeholder="选择开始日期"
                format="yyyy-MM-dd"
                value-format="yyyy-MM-dd">
              </el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="endDate">
              <el-date-picker
                v-model="backtestForm.endDate"
                type="date"
                placeholder="选择结束日期"
                format="yyyy-MM-dd"
                value-format="yyyy-MM-dd">
              </el-date-picker>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="初始资金" prop="initialCapital">
              <el-input-number
                v-model="backtestForm.initialCapital"
                :min="10000"
                :step="10000"
                :precision="0"
                style="width: 100%">
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手续费率" prop="commissionRate">
              <el-input-number
                v-model="backtestForm.commissionRate"
                :min="0"
                :max="0.01"
                :step="0.0001"
                :precision="4"
                style="width: 100%">
              </el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="滑点设置" prop="slippage">
              <el-input-number
                v-model="backtestForm.slippage"
                :min="0"
                :step="1"
                :precision="0"
                style="width: 100%">
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保证金率" prop="marginRate">
              <el-input-number
                v-model="backtestForm.marginRate"
                :min="0"
                :max="1"
                :step="0.01"
                :precision="2"
                style="width: 100%">
              </el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">策略参数</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="参数1" prop="param1">
              <el-input-number
                v-model="backtestForm.param1"
                :min="1"
                :step="1"
                :precision="0"
                style="width: 100%">
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="参数2" prop="param2">
              <el-input-number
                v-model="backtestForm.param2"
                :min="1"
                :step="1"
                :precision="0"
                style="width: 100%">
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="参数3" prop="param3">
              <el-input-number
                v-model="backtestForm.param3"
                :min="1"
                :step="1"
                :precision="0"
                style="width: 100%">
              </el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button type="primary" @click="submitBacktest('backtestForm')">开始回测</el-button>
          <el-button @click="resetForm('backtestForm')">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="box-card" style="margin-top: 20px;" v-if="showResult">
      <div slot="header" class="clearfix">
        <span>回测结果</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="exportResult">导出结果</el-button>
      </div>
      
      <div v-loading="backtestLoading">
        <el-row :gutter="20">
          <el-col :span="24">
            <div class="result-summary">
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-label">总收益率</div>
                    <div :class="['summary-value', backtestResult.totalReturn >= 0 ? 'profit' : 'loss']">
                      {{ backtestResult.totalReturn }}%
                    </div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-label">年化收益率</div>
                    <div :class="['summary-value', backtestResult.annualReturn >= 0 ? 'profit' : 'loss']">
                      {{ backtestResult.annualReturn }}%
                    </div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-label">夏普比率</div>
                    <div class="summary-value">
                      {{ backtestResult.sharpeRatio }}
                    </div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-label">最大回撤</div>
                    <div class="summary-value loss">
                      {{ backtestResult.maxDrawdown }}%
                    </div>
                  </div>
                </el-col>
              </el-row>
              
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-label">胜率</div>
                    <div class="summary-value">
                      {{ backtestResult.winRate }}%
                    </div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-label">盈亏比</div>
                    <div class="summary-value">
                      {{ backtestResult.profitLossRatio }}
                    </div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-label">交易次数</div>
                    <div class="summary-value">
                      {{ backtestResult.totalTrades }}
                    </div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-item">
                    <div class="summary-label">回测周期</div>
                    <div class="summary-value">
                      {{ backtestResult.period }}
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-col>
        </el-row>
        
        <el-divider></el-divider>
        
        <el-row :gutter="20">
          <el-col :span="24">
            <div id="equity-curve" class="chart-container"></div>
          </el-col>
        </el-row>
        
        <el-divider></el-divider>
        
        <el-row :gutter="20">
          <el-col :span="24">
            <el-tabs v-model="activeTab">
              <el-tab-pane label="交易记录" name="trades">
                <el-table
                  :data="backtestResult.trades"
                  style="width: 100%"
                  border>
                  <el-table-column prop="datetime" label="交易时间" width="180"></el-table-column>
                  <el-table-column prop="direction" label="方向" width="80">
                    <template slot-scope="scope">
                      <el-tag :type="scope.row.direction === 'LONG' ? 'danger' : 'success'">
                        {{ scope.row.direction === 'LONG' ? '买入' : '卖出' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="price" label="价格" width="100"></el-table-column>
                  <el-table-column prop="volume" label="数量" width="100"></el-table-column>
                  <el-table-column prop="turnover" label="成交额" width="120"></el-table-column>
                  <el-table-column prop="pnl" label="盈亏" width="120">
                    <template slot-scope="scope">
                      <span :class="scope.row.pnl >= 0 ? 'profit' : 'loss'">
                        {{ scope.row.pnl }}
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="commission" label="手续费" width="100"></el-table-column>
                  <el-table-column prop="slippage" label="滑点" width="100"></el-table-column>
                </el-table>
              </el-tab-pane>
              <el-tab-pane label="每日收益" name="daily">
                <el-table
                  :data="backtestResult.dailyResults"
                  style="width: 100%"
                  border>
                  <el-table-column prop="date" label="日期" width="120"></el-table-column>
                  <el-table-column prop="close" label="收盘价" width="100"></el-table-column>
                  <el-table-column prop="balance" label="账户余额" width="120"></el-table-column>
                  <el-table-column prop="return" label="日收益率" width="120">
                    <template slot-scope="scope">
                      <span :class="scope.row.return >= 0 ? 'profit' : 'loss'">
                        {{ scope.row.return }}%
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="cumulativeReturn" label="累计收益率" width="120">
                    <template slot-scope="scope">
                      <span :class="scope.row.cumulativeReturn >= 0 ? 'profit' : 'loss'">
                        {{ scope.row.cumulativeReturn }}%
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="drawdown" label="回撤" width="120">
                    <template slot-scope="scope">
                      <span :class="['loss', scope.row.drawdown === 0 ? 'zero-drawdown' : '']">
                        {{ scope.row.drawdown }}%
                      </span>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>
            </el-tabs>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Backtest',
  data() {
    return {
      backtestForm: {
        strategyName: '',
        strategyType: 'cta',
        symbol: '',
        interval: '1d',
        startDate: '',
        endDate: '',
        initialCapital: 100000,
        commissionRate: 0.0003,
        slippage: 1,
        marginRate: 0.1,
        param1: 10,
        param2: 20,
        param3: 30
      },
      rules: {
        strategyName: [{ required: true, message: '请输入策略名称', trigger: 'blur' }],
        strategyType: [{ required: true, message: '请选择策略类型', trigger: 'change' }],
        symbol: [{ required: true, message: '请选择交易品种', trigger: 'change' }],
        interval: [{ required: true, message: '请选择K线周期', trigger: 'change' }],
        startDate: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
        endDate: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
      },
      symbolOptions: [
        { value: '600000', label: '浦发银行 (600000)' },
        { value: '601398', label: '工商银行 (601398)' },
        { value: '000001', label: '平安银行 (000001)' },
        { value: '000858', label: '五粮液 (000858)' },
        { value: 'IF2106', label: '沪深300期货 (IF2106)' }
      ],
      showResult: false,
      backtestLoading: false,
      activeTab: 'trades',
      backtestResult: {
        totalReturn: 25.68,
        annualReturn: 12.34,
        sharpeRatio: 1.45,
        maxDrawdown: 15.67,
        winRate: 65.32,
        profitLossRatio: 1.78,
        totalTrades: 45,
        period: '2023-01-01 至 2023-12-31',
        trades: [
          {
            datetime: '2023-01-05 10:30:00',
            direction: 'LONG',
            price: 10.25,
            volume: 1000,
            turnover: 10250,
            pnl: 0,
            commission: 3.08,
            slippage: 10
          },
          {
            datetime: '2023-01-15 14:45:00',
            direction: 'SHORT',
            price: 11.05,
            volume: 1000,
            turnover: 11050,
            pnl: 800,
            commission: 3.32,
            slippage: 10
          },
          {
            datetime: '2023-02-10 09:30:00',
            direction: 'LONG',
            price: 10.50,
            volume: 1000,
            turnover: 10500,
            pnl: 0,
            commission: 3.15,
            slippage: 10
          }
        ],
        dailyResults: [
          {
            date: '2023-01-01',
            close: 10.15,
            balance: 100000,
            return: 0,
            cumulativeReturn: 0,
            drawdown: 0
          },
          {
            date: '2023-01-02',
            close: 10.20,
            balance: 100500,
            return: 0.5,
            cumulativeReturn: 0.5,
            drawdown: 0
          },
          {
            date: '2023-01-03',
            close: 10.18,
            balance: 100300,
            return: -0.2,
            cumulativeReturn: 0.3,
            drawdown: 0.2
          }
        ]
      }
    }
  },
  methods: {
    submitBacktest(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.backtestLoading = true;
          this.showResult = true;
          
          // 模拟API请求
          setTimeout(() => {
            this.backtestLoading = false;
            this.$message.success('回测完成');
            
            // 在实际项目中，这里应该初始化图表
            this.$nextTick(() => {
              this.initChart();
            });
          }, 2000);
        } else {
          this.$message.error('请完善回测参数');
          return false;
        }
      });
    },
    resetForm(formName) {
      this.$refs[formName].resetFields();
    },
    exportResult() {
      this.$message.success('回测结果已导出');
    },
    initChart() {
      // 在实际项目中，这里应该使用ECharts或其他图表库初始化图表
      console.log('初始化图表');
    }
  }
}
</script>

<style scoped>
.backtest-container {
  padding: 20px;
}
.result-summary {
  margin-bottom: 20px;
}
.summary-item {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
}
.summary-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}
.summary-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}
.profit {
  color: #f56c6c;
}
.loss {
  color: #67c23a;
}
.zero-drawdown {
  color: #909399;
}
.chart-container {
  height: 400px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}
.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both
}
</style>
