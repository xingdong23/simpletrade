<template>
  <div class="data-management">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <div slot="header">
            <h2>数据管理</h2>
          </div>
          
          <el-tabs v-model="activeTab">
            <el-tab-pane label="数据概览" name="overview">
              <el-table
                v-loading="loading"
                :data="dataOverview"
                style="width: 100%">
                <el-table-column
                  prop="symbol"
                  label="代码"
                  width="120">
                </el-table-column>
                <el-table-column
                  prop="exchange"
                  label="交易所"
                  width="120">
                </el-table-column>
                <el-table-column
                  prop="interval"
                  label="周期"
                  width="120">
                </el-table-column>
                <el-table-column
                  prop="count"
                  label="数据量"
                  width="120">
                </el-table-column>
                <el-table-column
                  prop="start"
                  label="开始日期"
                  width="180">
                </el-table-column>
                <el-table-column
                  prop="end"
                  label="结束日期"
                  width="180">
                </el-table-column>
                <el-table-column
                  prop="type"
                  label="类型"
                  width="120">
                </el-table-column>
                <el-table-column
                  label="操作">
                  <template slot-scope="scope">
                    <el-button
                      size="mini"
                      @click="viewData(scope.row)">查看</el-button>
                    <el-button
                      size="mini"
                      type="danger"
                      @click="deleteData(scope.row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="导入数据" name="import">
              <el-form ref="importForm" :model="importForm" label-width="120px">
                <el-form-item label="文件路径">
                  <el-input v-model="importForm.filePath" placeholder="请输入CSV文件路径"></el-input>
                </el-form-item>
                <el-form-item label="代码">
                  <el-input v-model="importForm.symbol" placeholder="例如：AAPL"></el-input>
                </el-form-item>
                <el-form-item label="交易所">
                  <el-select v-model="importForm.exchange" placeholder="请选择交易所">
                    <el-option label="NASDAQ" value="NASDAQ"></el-option>
                    <el-option label="NYSE" value="NYSE"></el-option>
                    <el-option label="SHFE" value="SHFE"></el-option>
                    <el-option label="CFFEX" value="CFFEX"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="周期">
                  <el-select v-model="importForm.interval" placeholder="请选择周期">
                    <el-option label="1分钟" value="1m"></el-option>
                    <el-option label="5分钟" value="5m"></el-option>
                    <el-option label="15分钟" value="15m"></el-option>
                    <el-option label="1小时" value="1h"></el-option>
                    <el-option label="日线" value="1d"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="importData">导入</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            
            <el-tab-pane label="导出数据" name="export">
              <el-form ref="exportForm" :model="exportForm" label-width="120px">
                <el-form-item label="代码">
                  <el-input v-model="exportForm.symbol" placeholder="例如：AAPL"></el-input>
                </el-form-item>
                <el-form-item label="交易所">
                  <el-select v-model="exportForm.exchange" placeholder="请选择交易所">
                    <el-option label="NASDAQ" value="NASDAQ"></el-option>
                    <el-option label="NYSE" value="NYSE"></el-option>
                    <el-option label="SHFE" value="SHFE"></el-option>
                    <el-option label="CFFEX" value="CFFEX"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="周期">
                  <el-select v-model="exportForm.interval" placeholder="请选择周期">
                    <el-option label="1分钟" value="1m"></el-option>
                    <el-option label="5分钟" value="5m"></el-option>
                    <el-option label="15分钟" value="15m"></el-option>
                    <el-option label="1小时" value="1h"></el-option>
                    <el-option label="日线" value="1d"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="开始日期">
                  <el-date-picker
                    v-model="exportForm.startDate"
                    type="date"
                    placeholder="选择开始日期"
                    format="yyyy-MM-dd"
                    value-format="yyyy-MM-dd">
                  </el-date-picker>
                </el-form-item>
                <el-form-item label="结束日期">
                  <el-date-picker
                    v-model="exportForm.endDate"
                    type="date"
                    placeholder="选择结束日期"
                    format="yyyy-MM-dd"
                    value-format="yyyy-MM-dd">
                  </el-date-picker>
                </el-form-item>
                <el-form-item label="文件路径">
                  <el-input v-model="exportForm.filePath" placeholder="请输入导出文件路径"></el-input>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="exportData">导出</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 数据查看对话框 -->
    <el-dialog title="数据查看" :visible.sync="dataDialogVisible" width="80%">
      <div v-if="currentData">
        <div id="kline-chart" style="width: 100%; height: 400px;"></div>
        
        <el-table
          :data="currentData.slice(0, 10)"
          style="width: 100%; margin-top: 20px;">
          <el-table-column
            prop="datetime"
            label="日期时间"
            width="180">
          </el-table-column>
          <el-table-column
            prop="open_price"
            label="开盘价"
            width="120">
          </el-table-column>
          <el-table-column
            prop="high_price"
            label="最高价"
            width="120">
          </el-table-column>
          <el-table-column
            prop="low_price"
            label="最低价"
            width="120">
          </el-table-column>
          <el-table-column
            prop="close_price"
            label="收盘价"
            width="120">
          </el-table-column>
          <el-table-column
            prop="volume"
            label="成交量"
            width="120">
          </el-table-column>
        </el-table>
        
        <div style="margin-top: 20px; color: #909399;">
          显示前10条数据，共 {{ currentData.length }} 条
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'DataManagement',
  data() {
    return {
      activeTab: 'overview',
      loading: false,
      dataDialogVisible: false,
      importForm: {
        filePath: '',
        symbol: '',
        exchange: '',
        interval: ''
      },
      exportForm: {
        symbol: '',
        exchange: '',
        interval: '',
        startDate: '',
        endDate: '',
        filePath: ''
      }
    }
  },
  computed: {
    ...mapState(['dataOverview', 'currentData'])
  },
  methods: {
    ...mapActions(['fetchDataOverview', 'fetchBarData']),
    
    async viewData(row) {
      this.loading = true
      
      try {
        await this.fetchBarData({
          symbol: row.symbol,
          exchange: row.exchange,
          interval: row.interval || '1d',
          startDate: row.start.split(' ')[0],
          endDate: row.end.split(' ')[0]
        })
        
        this.dataDialogVisible = true
        this.$nextTick(() => {
          this.renderKlineChart()
        })
      } catch (error) {
        this.$message.error('获取数据失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    deleteData(row) {
      this.$confirm('此操作将永久删除该数据, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const url = `http://localhost:8000/api/data/bars?symbol=${row.symbol}&exchange=${row.exchange}&interval=${row.interval || '1d'}`
          const response = await fetch(url, {
            method: 'DELETE'
          })
          const data = await response.json()
          
          if (data.success) {
            this.$message({
              type: 'success',
              message: '删除成功!'
            })
            this.fetchDataOverview()
          } else {
            this.$message.error(data.message || '删除失败')
          }
        } catch (error) {
          this.$message.error('删除失败: ' + error.message)
        }
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    
    async importData() {
      try {
        const response = await fetch('http://localhost:8000/api/data/import', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            file_path: this.importForm.filePath,
            symbol: this.importForm.symbol,
            exchange: this.importForm.exchange,
            interval: this.importForm.interval
          })
        })
        
        const data = await response.json()
        
        if (data.success) {
          this.$message({
            type: 'success',
            message: data.message || '导入成功'
          })
          this.fetchDataOverview()
          this.activeTab = 'overview'
        } else {
          this.$message.error(data.message || '导入失败')
        }
      } catch (error) {
        this.$message.error('导入失败: ' + error.message)
      }
    },
    
    async exportData() {
      try {
        const response = await fetch('http://localhost:8000/api/data/export', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            file_path: this.exportForm.filePath,
            symbol: this.exportForm.symbol,
            exchange: this.exportForm.exchange,
            interval: this.exportForm.interval,
            start_date: this.exportForm.startDate,
            end_date: this.exportForm.endDate
          })
        })
        
        const data = await response.json()
        
        if (data.success) {
          this.$message({
            type: 'success',
            message: data.message || '导出成功'
          })
        } else {
          this.$message.error(data.message || '导出失败')
        }
      } catch (error) {
        this.$message.error('导出失败: ' + error.message)
      }
    },
    
    renderKlineChart() {
      if (!this.currentData || this.currentData.length === 0) return
      
      const chartDom = document.getElementById('kline-chart')
      const myChart = this.$echarts.init(chartDom)
      
      const data = this.currentData.map(item => [
        item.datetime,
        item.open_price,
        item.close_price,
        item.low_price,
        item.high_price,
        item.volume
      ])
      
      const option = {
        title: {
          text: `${this.currentData[0].symbol} K线图`,
          left: 'center'
        },
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
          data: this.currentData.map(item => item.datetime),
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
            start: 50,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            top: '90%',
            start: 50,
            end: 100
          }
        ],
        series: [
          {
            name: 'K线',
            type: 'candlestick',
            data: this.currentData.map(item => [
              item.open_price,
              item.close_price,
              item.low_price,
              item.high_price
            ]),
            itemStyle: {
              color: '#ef232a',
              color0: '#14b143',
              borderColor: '#ef232a',
              borderColor0: '#14b143'
            }
          }
        ]
      }
      
      myChart.setOption(option)
    }
  },
  created() {
    this.loading = true
    this.fetchDataOverview().finally(() => {
      this.loading = false
    })
  }
}
</script>

<style scoped>
.data-management {
  min-height: calc(100vh - 120px);
}
</style>
