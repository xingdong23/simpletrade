<template>
  <div class="analysis-indicators">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <div slot="header">
            <h2>技术指标分析</h2>
          </div>
          
          <el-form ref="indicatorForm" :model="indicatorForm" label-width="120px">
            <el-row :gutter="10">
              <el-col :span="8">
                <el-form-item label="代码">
                  <el-input v-model="indicatorForm.symbol" placeholder="例如：AAPL"></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="交易所">
                  <el-select v-model="indicatorForm.exchange" placeholder="请选择交易所">
                    <el-option label="NASDAQ" value="NASDAQ"></el-option>
                    <el-option label="NYSE" value="NYSE"></el-option>
                    <el-option label="SHFE" value="SHFE"></el-option>
                    <el-option label="CFFEX" value="CFFEX"></el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="周期">
                  <el-select v-model="indicatorForm.interval" placeholder="请选择周期">
                    <el-option label="1分钟" value="1m"></el-option>
                    <el-option label="5分钟" value="5m"></el-option>
                    <el-option label="15分钟" value="15m"></el-option>
                    <el-option label="1小时" value="1h"></el-option>
                    <el-option label="日线" value="1d"></el-option>
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="10">
                <el-col :span="8">
                    <el-form-item label="开始日期">
                    <el-date-picker
                        v-model="indicatorForm.startDate"
                        type="date"
                        placeholder="选择开始日期"
                        style="width: 100%;"
                        format="yyyy-MM-dd"
                        value-format="yyyy-MM-dd">
                    </el-date-picker>
                    </el-form-item>
                </el-col>
                <el-col :span="8">
                    <el-form-item label="结束日期">
                    <el-date-picker
                        v-model="indicatorForm.endDate"
                        type="date"
                        style="width: 100%;"
                        placeholder="选择结束日期"
                        format="yyyy-MM-dd"
                        value-format="yyyy-MM-dd">
                    </el-date-picker>
                    </el-form-item>
                </el-col>
            </el-row>

            <el-form-item label="技术指标">
              <el-checkbox-group v-model="indicatorForm.selectedIndicators">
                 <el-row>
                    <el-col :span="6">
                        <el-checkbox label="SMA">简单移动平均线 (SMA)</el-checkbox>
                        <el-input-number v-model="indicatorForm.params.SMA.period" size="mini" :min="1" label="周期" v-if="indicatorForm.selectedIndicators.includes('SMA')"></el-input-number>
                    </el-col>
                    <el-col :span="6">
                        <el-checkbox label="EMA">指数移动平均线 (EMA)</el-checkbox>
                        <el-input-number v-model="indicatorForm.params.EMA.period" size="mini" :min="1" label="周期" v-if="indicatorForm.selectedIndicators.includes('EMA')"></el-input-number>
                    </el-col>
                     <el-col :span="6">
                         <el-checkbox label="MACD">MACD</el-checkbox>
                         <div v-if="indicatorForm.selectedIndicators.includes('MACD')">
                            <el-input-number v-model="indicatorForm.params.MACD.fast_period" size="mini" :min="1" label="快线"></el-input-number>
                            <el-input-number v-model="indicatorForm.params.MACD.slow_period" size="mini" :min="1" label="慢线"></el-input-number>
                            <el-input-number v-model="indicatorForm.params.MACD.signal_period" size="mini" :min="1" label="信号"></el-input-number>
                         </div>
                    </el-col>
                    <el-col :span="6">
                         <el-checkbox label="RSI">RSI</el-checkbox>
                         <el-input-number v-model="indicatorForm.params.RSI.period" size="mini" :min="1" label="周期" v-if="indicatorForm.selectedIndicators.includes('RSI')"></el-input-number>
                    </el-col>
                </el-row>
                <el-row>
                    <el-col :span="6">
                         <el-checkbox label="BOLL">布林带 (BOLL)</el-checkbox>
                         <div v-if="indicatorForm.selectedIndicators.includes('BOLL')">
                             <el-input-number v-model="indicatorForm.params.BOLL.period" size="mini" :min="1" label="周期"></el-input-number>
                             <el-input-number v-model="indicatorForm.params.BOLL.dev" size="mini" :min="1" :step="0.1" label="标准差"></el-input-number>
                         </div>
                    </el-col>
                    <!-- Add more indicators here -->
                 </el-row>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="calculateIndicators" :loading="loading">计算指标</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Analysis Result Section -->
    <el-row :gutter="20" style="margin-top: 20px;" v-if="analysisResults">
      <el-col :span="24">
        <el-card>
          <div slot="header">
            <h3>分析结果</h3>
          </div>
          <!-- Keep only indicator results -->
          <div>
            <div id="indicator-chart" style="width: 100%; height: 500px;"></div>
            <!-- Potentially add a table for indicator values -->
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'AnalysisIndicators',
  data() {
    return {
      loading: false,
      indicatorForm: {
        symbol: '',
        exchange: '',
        interval: '1d',
        startDate: '',
        endDate: '',
        selectedIndicators: [],
        params: {
          SMA: { period: 20 },
          EMA: { period: 20 },
          MACD: { fast_period: 12, slow_period: 26, signal_period: 9 },
          RSI: { period: 14 },
          BOLL: { period: 20, dev: 2 },
        }
      },
      analysisResults: null
    }
  },
  computed: {
    // ...mapState(['analysisResults']),
  },
  methods: {
    ...mapActions(['fetchIndicatorData']),
    
    async calculateIndicators() {
      this.loading = true;
      this.analysisResults = null;

      try {
        const requestParams = {
          symbol: this.indicatorForm.symbol,
          exchange: this.indicatorForm.exchange,
          interval: this.indicatorForm.interval,
          start_date: this.indicatorForm.startDate,
          end_date: this.indicatorForm.endDate,
          indicators: {}
        };
        
        this.indicatorForm.selectedIndicators.forEach(indicator => {
            if (this.indicatorForm.params[indicator]) {
                 requestParams.indicators[indicator] = this.indicatorForm.params[indicator];
            }
        });
        
        if (Object.keys(requestParams.indicators).length === 0) {
             this.$message.warning('请至少选择一个技术指标');
             this.loading = false;
             return;
        }

        const results = await this.fetchIndicatorData(requestParams);
        this.analysisResults = results;

        this.$nextTick(() => {
          this.renderIndicatorChart();
        });

      } catch (error) {
        console.error("Error calculating indicators:", error);
        this.$message.error('计算指标失败: ' + (error.message || error));
        this.analysisResults = null;
      } finally {
        this.loading = false;
      }
    },
    
    renderIndicatorChart() {
      if (!this.analysisResults || !window.echarts) {
        console.error('无法渲染指标图表：结果或echarts未准备好');
        return;
      }
      
      const chartDom = document.getElementById('indicator-chart');
       if (!chartDom) {
        console.error('无法找到指标图表容器');
        return;
      }
      const myChart = window.echarts.init(chartDom);

      const klineData = this.analysisResults.kline || [];
      const indicatorData = this.analysisResults.indicators || {};
      const categoryData = klineData.map(item => item.datetime);
      const klineValues = klineData.map(item => [item.open, item.close, item.low, item.high]);
      const volumes = klineData.map(item => item.volume);
      
      const legendData = ['K线', '成交量', ...Object.keys(indicatorData)];
      const series = [];
      
      series.push({
        name: 'K线',
        type: 'candlestick',
        data: klineValues,
         itemStyle: {
            color: '#ec0000', color0: '#00da3c', 
            borderColor: '#8A0000', borderColor0: '#008F28'
         },
      });
      
      series.push({
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: {
            color: (params) => klineValues[params.dataIndex][1] >= klineValues[params.dataIndex][0] ? '#ec0000' : '#00da3c'
        }
      });

      if (indicatorData.SMA_20) {
          series.push({ name: 'SMA_20', type: 'line', data: indicatorData.SMA_20, smooth: true, showSymbol: false });
      }
       if (indicatorData.EMA_20) {
          series.push({ name: 'EMA_20', type: 'line', data: indicatorData.EMA_20, smooth: true, showSymbol: false });
      }
      if (indicatorData.MACD) {
           series.push({ name: 'MACD', type: 'line', data: indicatorData.MACD.macd, smooth: true, showSymbol: false, yAxisIndex: 2 });
           series.push({ name: 'Signal', type: 'line', data: indicatorData.MACD.signal, smooth: true, showSymbol: false, yAxisIndex: 2 });
           series.push({ name: 'Hist', type: 'bar', data: indicatorData.MACD.hist, yAxisIndex: 2 });
      }

      const option = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        legend: { data: legendData },
        grid: [
          { left: '10%', right: '8%', height: '50%' },
          { left: '10%', right: '8%', top: '65%', height: '15%' },
          { left: '10%', right: '8%', top: '82%', height: '15%' }
        ],
        xAxis: [
          { type: 'category', data: categoryData, scale: true, boundaryGap: false, axisLine: { onZero: false }, splitLine: { show: false }, min: 'dataMin', max: 'dataMax' },
          { type: 'category', gridIndex: 1, data: categoryData, scale: true, boundaryGap: false, axisLine: { onZero: false }, axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false }, min: 'dataMin', max: 'dataMax' },
           { type: 'category', gridIndex: 2, data: categoryData, scale: true, boundaryGap: false, axisLine: { onZero: false }, axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false }, min: 'dataMin', max: 'dataMax' }
        ],
        yAxis: [
          { scale: true, splitArea: { show: true } },
          { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { show: false }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { show: false } },
          { scale: true, gridIndex: 2, splitNumber: 3, axisLabel: { show: true }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { show: false } }
        ],
        dataZoom: [
          { type: 'inside', xAxisIndex: [0, 1, 2], start: 80, end: 100 },
          { show: true, xAxisIndex: [0, 1, 2], type: 'slider', bottom: '10px', start: 80, end: 100 }
        ],
        series: series
      };

      myChart.setOption(option);

      window.addEventListener('resize', () => { myChart.resize(); });
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', () => { myChart.resize(); });
        myChart.dispose();
      });
    }
  },
  created() {
    // Initial setup if needed
  }
}
</script>

<style scoped>
.analysis-indicators {
  padding: 20px;
}
#indicator-chart {
  /* Ensure height is set */
}
.el-checkbox-group .el-col {
    margin-bottom: 10px;
}
.el-checkbox-group .el-input-number {
    margin-left: 10px;
    width: 100px;
}
.el-checkbox-group .el-col > * {
    vertical-align: middle;
}
.el-checkbox-group .el-col > div {
    display: inline-block;
    vertical-align: middle;
    margin-left: 10px;
}
.el-checkbox-group .el-col > div .el-input-number {
    margin-left: 5px;
     margin-right: 5px;
}
</style>
