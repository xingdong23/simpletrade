<template>
  <div class="analysis">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <div slot="header">
            <h2>数据分析</h2>
          </div>
          
          <el-tabs v-model="activeTab">
            <el-tab-pane label="技术指标" name="indicators">
              <el-form ref="indicatorForm" :model="indicatorForm" label-width="120px">
                <el-form-item label="代码">
                  <el-input v-model="indicatorForm.symbol" placeholder="例如：AAPL"></el-input>
                </el-form-item>
                <el-form-item label="交易所">
                  <el-select v-model="indicatorForm.exchange" placeholder="请选择交易所">
                    <el-option label="NASDAQ" value="NASDAQ"></el-option>
                    <el-option label="NYSE" value="NYSE"></el-option>
                    <el-option label="SHFE" value="SHFE"></el-option>
                    <el-option label="CFFEX" value="CFFEX"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="周期">
                  <el-select v-model="indicatorForm.interval" placeholder="请选择周期">
                    <el-option label="1分钟" value="1m"></el-option>
                    <el-option label="5分钟" value="5m"></el-option>
                    <el-option label="15分钟" value="15m"></el-option>
                    <el-option label="1小时" value="1h"></el-option>
                    <el-option label="日线" value="1d"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="开始日期">
                  <el-date-picker
                    v-model="indicatorForm.startDate"
                    type="date"
                    placeholder="选择开始日期"
                    format="yyyy-MM-dd"
                    value-format="yyyy-MM-dd">
                  </el-date-picker>
                </el-form-item>
                <el-form-item label="结束日期">
                  <el-date-picker
                    v-model="indicatorForm.endDate"
                    type="date"
                    placeholder="选择结束日期"
                    format="yyyy-MM-dd"
                    value-format="yyyy-MM-dd">
                  </el-date-picker>
                </el-form-item>
                <el-form-item label="技术指标">
                  <el-checkbox-group v-model="indicatorForm.selectedIndicators">
                    <el-checkbox label="SMA">简单移动平均线</el-checkbox>
                    <el-checkbox label="EMA">指数移动平均线</el-checkbox>
                    <el-checkbox label="MACD">MACD</el-checkbox>
                    <el-checkbox label="RSI">RSI</el-checkbox>
                    <el-checkbox label="BOLL">布林带</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="calculateIndicators" :loading="loading">计算指标</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            
            <el-tab-pane label="策略回测" name="backtest">
              <el-form ref="backtestForm" :model="backtestForm" label-width="120px">
                <el-form-item label="代码">
                  <el-input v-model="backtestForm.symbol" placeholder="例如：AAPL"></el-input>
                </el-form-item>
                <el-form-item label="交易所">
                  <el-select v-model="backtestForm.exchange" placeholder="请选择交易所">
                    <el-option label="NASDAQ" value="NASDAQ"></el-option>
                    <el-option label="NYSE" value="NYSE"></el-option>
                    <el-option label="SHFE" value="SHFE"></el-option>
                    <el-option label="CFFEX" value="CFFEX"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="周期">
                  <el-select v-model="backtestForm.interval" placeholder="请选择周期">
                    <el-option label="1分钟" value="1m"></el-option>
                    <el-option label="5分钟" value="5m"></el-option>
                    <el-option label="15分钟" value="15m"></el-option>
                    <el-option label="1小时" value="1h"></el-option>
                    <el-option label="日线" value="1d"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="开始日期">
                  <el-date-picker
                    v-model="backtestForm.startDate"
                    type="date"
                    placeholder="选择开始日期"
                    format="yyyy-MM-dd"
                    value-format="yyyy-MM-dd">
                  </el-date-picker>
                </el-form-item>
                <el-form-item label="结束日期">
                  <el-date-picker
                    v-model="backtestForm.endDate"
                    type="date"
                    placeholder="选择结束日期"
                    format="yyyy-MM-dd"
                    value-format="yyyy-MM-dd">
                  </el-date-picker>
                </el-form-item>
                <el-form-item label="策略">
                  <el-select v-model="backtestForm.strategy" placeholder="请选择策略">
                    <el-option label="移动平均线交叉" value="MovingAverageCrossover"></el-option>
                    <el-option label="RSI策略" value="RSIStrategy"></el-option>
                    <el-option label="布林带策略" value="BollingerBandsStrategy"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="初始资金">
                  <el-input-number v-model="backtestForm.initialCapital" :min="1000" :step="1000"></el-input-number>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="runBacktest" :loading="loading">运行回测</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 分析结果 -->
    <el-row :gutter="20" style="margin-top: 20px;" v-if="analysisResults">
      <el-col :span="24">
        <el-card>
          <div slot="header">
            <h3>分析结果</h3>
          </div>
          
          <!-- 技术指标结果 -->
          <div v-if="activeTab === 'indicators'">
            <div id="indicator-chart" style="width: 100%; height: 500px;"></div>
          </div>
          
          <!-- 回测结果 -->
          <div v-if="activeTab === 'backtest' && backtestResults">
            <el-row :gutter="20">
              <el-col :span="12">
                <h4>回测摘要</h4>
                <el-descriptions border>
                  <el-descriptions-item label="总交易次数">{{ backtestResults.summary.total_trades }}</el-descriptions-item>
                  <el-descriptions-item label="盈利交易">{{ backtestResults.summary.winning_trades }}</el-descriptions-item>
                  <el-descriptions-item label="亏损交易">{{ backtestResults.summary.losing_trades }}</el-descriptions-item>
                  <el-descriptions-item label="胜率">{{ (backtestResults.summary.win_rate * 100).toFixed(2) }}%</el-descriptions-item>
                  <el-descriptions-item label="总收益">{{ backtestResults.summary.total_profit.toFixed(2) }}</el-descriptions-item>
                  <el-descriptions-item label="收益率">{{ backtestResults.summary.return_pct.toFixed(2) }}%</el-descriptions-item>
                  <el-descriptions-item label="最大回撤">{{ backtestResults.summary.max_drawdown.toFixed(2) }}</el-descriptions-item>
                  <el-descriptions-item label="最大回撤率">{{ (backtestResults.summary.max_drawdown_pct * 100).toFixed(2) }}%</el-descriptions-item>
                  <el-descriptions-item label="初始资金">{{ backtestResults.summary.initial_capital.toFixed(2) }}</el-descriptions-item>
                  <el-descriptions-item label="最终资金">{{ backtestResults.summary.final_capital.toFixed(2) }}</el-descriptions-item>
                </el-descriptions>
              </el-col>
              <el-col :span="12">
                <h4>资金曲线</h4>
                <div id="equity-chart" style="width: 100%; height: 300px;"></div>
              </el-col>
            </el-row>
            
            <h4 style="margin-top: 20px;">交易记录</h4>
            <el-table
              :data="backtestResults.trades.slice(0, 10)"
              style="width: 100%">
              <el-table-column
                prop="datetime"
                label="日期时间"
                width="180">
              </el-table-column>
              <el-table-column
                prop="type"
                label="类型"
                width="120">
              </el-table-column>
              <el-table-column
                prop="price"
                label="价格"
                width="120">
              </el-table-column>
              <el-table-column
                prop="profit"
                label="收益">
                <template slot-scope="scope">
                  <span :style="{ color: scope.row.profit > 0 ? '#14b143' : scope.row.profit < 0 ? '#ef232a' : '' }">
                    {{ scope.row.profit.toFixed(2) }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
            
            <div style="margin-top: 20px; color: #909399;" v-if="backtestResults.trades.length > 10">
              显示前10条交易记录，共 {{ backtestResults.trades.length }} 条
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Analysis',
  data() {
    return {
      activeTab: 'indicators',
      loading: false,
      indicatorForm: {
        symbol: '',
        exchange: '',
        interval: '',
        startDate: '',
        endDate: '',
        selectedIndicators: []
      },
      backtestForm: {
        symbol: '',
        exchange: '',
        interval: '',
        startDate: '',
        endDate: '',
        strategy: '',
        initialCapital: 100000
      },
      backtestResults: null
    }
  },
  computed: {
    ...mapState(['analysisResults']),
    
    indicatorParams() {
      const params = {}
      
      if (this.indicatorForm.selectedIndicators.includes('SMA')) {
        params.SMA = { period: 20 }
      }
      
      if (this.indicatorForm.selectedIndicators.includes('EMA')) {
        params.EMA = { period: 20 }
      }
      
      if (this.indicatorForm.selectedIndicators.includes('MACD')) {
        params.MACD = {
          fast_period: 12,
          slow_period: 26,
          signal_period: 9
        }
      }
      
      if (this.indicatorForm.selectedIndicators.includes('RSI')) {
        params.RSI = { period: 14 }
      }
      
      if (this.indicatorForm.selectedIndicators.includes('BOLL')) {
        params.BOLL = {
          period: 20,
          std_dev: 2
        }
      }
      
      return params
    },
    
    strategyParams() {
      if (this.backtestForm.strategy === 'MovingAverageCrossover') {
        return {
          fast_period: 5,
          slow_period: 20
        }
      } else if (this.backtestForm.strategy === 'RSIStrategy') {
        return {
          period: 14,
          overbought: 70,
          oversold: 30
        }
      } else if (this.backtestForm.strategy === 'BollingerBandsStrategy') {
        return {
          period: 20,
          std_dev: 2
        }
      }
      
      return {}
    }
  },
  methods: {
    ...mapActions(['calculateIndicators', 'runBacktest']),
    
    async calculateIndicators() {
      if (!this.indicatorForm.symbol || !this.indicatorForm.exchange || !this.indicatorForm.interval || !this.indicatorForm.startDate || this.indicatorForm.selectedIndicators.length === 0) {
        this.$message.warning('请填写完整的表单')
        return
      }
      
      this.loading = true
      
      try {
        const indicators = []
        
        for (const indicator of this.indicatorForm.selectedIndicators) {
          if (indicator === 'SMA') {
            indicators.push({ name: 'SMA', params: { period: 20 } })
          } else if (indicator === 'EMA') {
            indicators.push({ name: 'EMA', params: { period: 20 } })
          } else if (indicator === 'MACD') {
            indicators.push({
              name: 'MACD',
              params: {
                fast_period: 12,
                slow_period: 26,
                signal_period: 9
              }
            })
          } else if (indicator === 'RSI') {
            indicators.push({ name: 'RSI', params: { period: 14 } })
          } else if (indicator === 'BOLL') {
            indicators.push({
              name: 'BOLL',
              params: {
                period: 20,
                std_dev: 2
              }
            })
          }
        }
        
        const payload = {
          symbol: this.indicatorForm.symbol,
          exchange: this.indicatorForm.exchange,
          interval: this.indicatorForm.interval,
          start_date: this.indicatorForm.startDate,
          end_date: this.indicatorForm.endDate,
          indicators: indicators
        }
        
        const result = await fetch('http://localhost:8000/api/analysis/indicators', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })
        
        const data = await result.json()
        
        if (data.success) {
          this.$store.commit('setAnalysisResults', data.data)
          this.$nextTick(() => {
            this.renderIndicatorChart()
          })
        } else {
          this.$message.error(data.message || '计算指标失败')
        }
      } catch (error) {
        this.$message.error('计算指标失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    async runBacktest() {
      if (!this.backtestForm.symbol || !this.backtestForm.exchange || !this.backtestForm.interval || !this.backtestForm.startDate || !this.backtestForm.strategy) {
        this.$message.warning('请填写完整的表单')
        return
      }
      
      this.loading = true
      
      try {
        const payload = {
          symbol: this.backtestForm.symbol,
          exchange: this.backtestForm.exchange,
          interval: this.backtestForm.interval,
          start_date: this.backtestForm.startDate,
          end_date: this.backtestForm.endDate,
          strategy_name: this.backtestForm.strategy,
          strategy_params: this.strategyParams,
          initial_capital: this.backtestForm.initialCapital
        }
        
        const result = await fetch('http://localhost:8000/api/analysis/backtest', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })
        
        const data = await result.json()
        
        if (data.success) {
          this.backtestResults = data.data
          this.$nextTick(() => {
            this.renderEquityChart()
          })
        } else {
          this.$message.error(data.message || '回测失败')
        }
      } catch (error) {
        this.$message.error('回测失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    renderIndicatorChart() {
      if (!this.analysisResults || this.analysisResults.length === 0) return
      
      const chartDom = document.getElementById('indicator-chart')
      const myChart = this.$echarts.init(chartDom)
      
      const dates = this.analysisResults.map(item => item.datetime)
      const prices = this.analysisResults.map(item => item.close)
      
      const series = [
        {
          name: '收盘价',
          type: 'line',
          data: prices,
          showSymbol: false,
          lineStyle: {
            width: 1
          }
        }
      ]
      
      // 添加技术指标
      for (const indicator of this.indicatorForm.selectedIndicators) {
        if (indicator === 'SMA') {
          series.push({
            name: 'SMA(20)',
            type: 'line',
            data: this.analysisResults.map(item => item.SMA_20),
            showSymbol: false,
            lineStyle: {
              width: 1
            }
          })
        } else if (indicator === 'EMA') {
          series.push({
            name: 'EMA(20)',
            type: 'line',
            data: this.analysisResults.map(item => item.EMA_20),
            showSymbol: false,
            lineStyle: {
              width: 1
            }
          })
        } else if (indicator === 'MACD') {
          // MACD需要单独处理，因为它有三个值
          const macdChart = {
            grid: {
              left: '10%',
              right: '10%',
              bottom: '15%',
              height: '30%'
            },
            xAxis: {
              type: 'category',
              data: dates,
              show: false
            },
            yAxis: {
              scale: true,
              splitArea: {
                show: false
              }
            },
            series: [
              {
                name: 'MACD',
                type: 'line',
                data: this.analysisResults.map(item => item.MACD),
                showSymbol: false,
                lineStyle: {
                  width: 1,
                  color: '#ff9800'
                }
              },
              {
                name: 'Signal',
                type: 'line',
                data: this.analysisResults.map(item => item.MACD_Signal),
                showSymbol: false,
                lineStyle: {
                  width: 1,
                  color: '#2196f3'
                }
              },
              {
                name: 'Histogram',
                type: 'bar',
                data: this.analysisResults.map(item => item.MACD_Hist),
                itemStyle: {
                  color: function(params) {
                    return params.data >= 0 ? '#14b143' : '#ef232a'
                  }
                }
              }
            ]
          }
        } else if (indicator === 'RSI') {
          // RSI需要单独处理，因为它的值范围是0-100
          const rsiChart = {
            grid: {
              left: '10%',
              right: '10%',
              bottom: '15%',
              height: '30%'
            },
            xAxis: {
              type: 'category',
              data: dates,
              show: false
            },
            yAxis: {
              scale: true,
              min: 0,
              max: 100,
              splitArea: {
                show: false
              }
            },
            series: [
              {
                name: 'RSI(14)',
                type: 'line',
                data: this.analysisResults.map(item => item.RSI_14),
                showSymbol: false,
                lineStyle: {
                  width: 1,
                  color: '#9c27b0'
                }
              },
              {
                name: '超买线',
                type: 'line',
                data: Array(dates.length).fill(70),
                showSymbol: false,
                lineStyle: {
                  width: 1,
                  type: 'dashed',
                  color: '#ef232a'
                }
              },
              {
                name: '超卖线',
                type: 'line',
                data: Array(dates.length).fill(30),
                showSymbol: false,
                lineStyle: {
                  width: 1,
                  type: 'dashed',
                  color: '#14b143'
                }
              }
            ]
          }
        } else if (indicator === 'BOLL') {
          series.push({
            name: '布林上轨',
            type: 'line',
            data: this.analysisResults.map(item => item.BOLL_Upper),
            showSymbol: false,
            lineStyle: {
              width: 1,
              type: 'dashed'
            }
          })
          
          series.push({
            name: '布林中轨',
            type: 'line',
            data: this.analysisResults.map(item => item.BOLL_Middle),
            showSymbol: false,
            lineStyle: {
              width: 1
            }
          })
          
          series.push({
            name: '布林下轨',
            type: 'line',
            data: this.analysisResults.map(item => item.BOLL_Lower),
            showSymbol: false,
            lineStyle: {
              width: 1,
              type: 'dashed'
            }
          })
        }
      }
      
      const option = {
        title: {
          text: `${this.indicatorForm.symbol} 技术指标分析`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: series.map(item => item.name),
          top: 30
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%'
        },
        xAxis: {
          type: 'category',
          data: dates,
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          splitNumber: 20
        },
        yAxis: {
          scale: true,
          splitArea: {
            show: true
          }
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            top: '90%',
            start: 0,
            end: 100
          }
        ],
        series: series
      }
      
      myChart.setOption(option)
    },
    
    renderEquityChart() {
      if (!this.backtestResults || !this.backtestResults.equity_curve || this.backtestResults.equity_curve.length === 0) return
      
      const chartDom = document.getElementById('equity-chart')
      const myChart = this.$echarts.init(chartDom)
      
      const dates = this.backtestResults.equity_curve.map(item => item.datetime)
      const capitals = this.backtestResults.equity_curve.map(item => item.capital)
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%'
        },
        xAxis: {
          type: 'category',
          data: dates,
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          splitNumber: 20
        },
        yAxis: {
          scale: true,
          splitArea: {
            show: true
          }
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            top: '90%',
            start: 0,
            end: 100
          }
        ],
        series: [
          {
            name: '资金',
            type: 'line',
            data: capitals,
            showSymbol: false,
            lineStyle: {
              width: 1,
              color: '#2196f3'
            }
          }
        ]
      }
      
      myChart.setOption(option)
    }
  }
}
</script>

<style scoped>
.analysis {
  min-height: calc(100vh - 120px);
}
</style>
