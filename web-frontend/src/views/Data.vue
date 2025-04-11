<template>
  <div class="data-management">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <div slot="header">
            <h2>数据概览</h2>
          </div>
          
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
  name: 'DataOverview',
  data() {
    return {
      loading: false,
      dataDialogVisible: false
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
        this.$message.error('获取数据失败: ' + (error.message || error))
      } finally {
        this.loading = false
      }
    },
    
    deleteData(row) {
      this.$confirm(`确定删除 ${row.symbol} (${row.interval}) 的数据吗?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        console.log('Delete data:', row)
        this.$message({
          type: 'success',
          message: '删除请求已发送!'
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    
    renderKlineChart() {
      if (!this.currentData || !window.echarts) {
        console.error('无法渲染K线图：数据或echarts未准备好')
        return
      }
      
      const chartDom = document.getElementById('kline-chart')
      if (!chartDom) {
        console.error('无法找到K线图容器')
        return
      }
      
      const myChart = window.echarts.init(chartDom)
      
      const categoryData = []
      const values = []
      const volumes = []
      this.currentData.forEach(item => {
        categoryData.push(item.datetime)
        values.push([item.open_price, item.close_price, item.low_price, item.high_price])
        volumes.push(item.volume)
      })

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['K线', '成交量']
        },
        grid: [
          {
            left: '10%',
            right: '8%',
            height: '50%'
          },
          {
            left: '10%',
            right: '8%',
            top: '65%',
            height: '15%'
          }
        ],
        xAxis: [
          {
            type: 'category',
            data: categoryData,
            scale: true,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false },
            min: 'dataMin',
            max: 'dataMax'
          },
          {
            type: 'category',
            gridIndex: 1,
            data: categoryData,
            scale: true,
            boundaryGap: false,
            axisLine: { onZero: false },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { show: false },
            min: 'dataMin',
            max: 'dataMax'
          }
        ],
        yAxis: [
          {
            scale: true,
            splitArea: {
              show: true
            }
          },
          {
            scale: true,
            gridIndex: 1,
            splitNumber: 2,
            axisLabel: { show: false },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false }
          }
        ],
        dataZoom: [
          {
            type: 'inside',
            xAxisIndex: [0, 1],
            start: 80,
            end: 100
          },
          {
            show: true,
            xAxisIndex: [0, 1],
            type: 'slider',
            top: '85%',
            start: 80,
            end: 100
          }
        ],
        series: [
          {
            name: 'K线',
            type: 'candlestick',
            data: values,
            itemStyle: {
              color: '#ec0000',
              color0: '#00da3c',
              borderColor: '#8A0000',
              borderColor0: '#008F28'
            },
            markPoint: {
              data: [
                {
                  type: 'max',
                  name: '最大值',
                  valueDim: 'highest'
                },
                {
                  type: 'min',
                  name: '最小值',
                  valueDim: 'lowest'
                }
              ]
            },
          },
          {
            name: '成交量',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: volumes,
            itemStyle: {
              color: function (params) {
                const klineData = values[params.dataIndex]
                return klineData[1] >= klineData[0] ? '#ec0000' : '#00da3c'
              }
            }
          }
        ]
      }

      myChart.setOption(option)
      
      window.addEventListener('resize', () => {
        myChart.resize()
      })
      
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', () => { myChart.resize() })
        myChart.dispose()
      })
    },
    
    loadDataOverview() {
      this.loading = true
      this.fetchDataOverview()
        .catch(error => {
          this.$message.error('加载数据概览失败: ' + (error.message || error))
        })
        .finally(() => {
          this.loading = false
        })
    }
  },
  created() {
    this.loadDataOverview()
  }
}
</script>

<style scoped>
.data-management {
  min-height: calc(100vh - 120px)
}

#kline-chart {
  /* Ensure height is set for ECharts */
}
</style>
