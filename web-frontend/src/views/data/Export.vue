<template>
  <div class="data-export-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>数据导出</span>
      </div>
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="数据类型">
          <el-select v-model="exportForm.dataType" placeholder="请选择数据类型">
            <el-option label="K线数据" value="kline"></el-option>
            <el-option label="Tick数据" value="tick"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="交易所">
          <el-select v-model="exportForm.exchange" placeholder="请选择交易所">
            <el-option label="上海证券交易所" value="SSE"></el-option>
            <el-option label="深圳证券交易所" value="SZSE"></el-option>
            <el-option label="中国金融期货交易所" value="CFFEX"></el-option>
            <el-option label="上海期货交易所" value="SHFE"></el-option>
            <el-option label="大连商品交易所" value="DCE"></el-option>
            <el-option label="郑州商品交易所" value="CZCE"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="合约代码">
          <el-input v-model="exportForm.symbol" placeholder="请输入合约代码"></el-input>
        </el-form-item>
        
        <el-form-item label="时间周期" v-if="exportForm.dataType === 'kline'">
          <el-select v-model="exportForm.interval" placeholder="请选择时间周期">
            <el-option label="1分钟" value="1m"></el-option>
            <el-option label="5分钟" value="5m"></el-option>
            <el-option label="15分钟" value="15m"></el-option>
            <el-option label="30分钟" value="30m"></el-option>
            <el-option label="1小时" value="1h"></el-option>
            <el-option label="日线" value="1d"></el-option>
            <el-option label="周线" value="1w"></el-option>
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
        
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportForm.format">
            <el-radio label="csv">CSV</el-radio>
            <el-radio label="excel">Excel</el-radio>
            <el-radio label="json">JSON</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitExport">导出数据</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="box-card" style="margin-top: 20px;">
      <div slot="header" class="clearfix">
        <span>导出历史</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="refreshHistory">刷新</el-button>
      </div>
      <el-table :data="exportHistory" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="dataType" label="数据类型" width="100"></el-table-column>
        <el-table-column prop="symbol" label="合约代码" width="120"></el-table-column>
        <el-table-column prop="dateRange" label="日期范围"></el-table-column>
        <el-table-column prop="format" label="格式" width="80"></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === '完成' ? 'success' : scope.row.status === '处理中' ? 'warning' : 'danger'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180"></el-table-column>
        <el-table-column label="操作" width="120">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              :disabled="scope.row.status !== '完成'"
              @click="downloadFile(scope.row)">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'DataExport',
  data() {
    return {
      exportForm: {
        dataType: 'kline',
        exchange: '',
        symbol: '',
        interval: '1d',
        startDate: '',
        endDate: '',
        format: 'csv'
      },
      exportHistory: [
        {
          id: 1,
          dataType: 'K线数据',
          symbol: '600000',
          dateRange: '2023-01-01 至 2023-12-31',
          format: 'CSV',
          status: '完成',
          createTime: '2024-04-10 10:30:00'
        },
        {
          id: 2,
          dataType: 'Tick数据',
          symbol: '000001',
          dateRange: '2023-06-01 至 2023-06-30',
          format: 'Excel',
          status: '处理中',
          createTime: '2024-04-12 15:45:00'
        }
      ]
    }
  },
  methods: {
    submitExport() {
      // 调用API导出数据
      this.$message({
        message: '数据导出请求已提交，请等待处理',
        type: 'success'
      });
      
      // 模拟添加到导出历史
      const newExport = {
        id: this.exportHistory.length + 1,
        dataType: this.exportForm.dataType === 'kline' ? 'K线数据' : 'Tick数据',
        symbol: this.exportForm.symbol,
        dateRange: `${this.exportForm.startDate} 至 ${this.exportForm.endDate}`,
        format: this.exportForm.format.toUpperCase(),
        status: '处理中',
        createTime: new Date().toLocaleString()
      };
      this.exportHistory.unshift(newExport);
    },
    resetForm() {
      this.exportForm = {
        dataType: 'kline',
        exchange: '',
        symbol: '',
        interval: '1d',
        startDate: '',
        endDate: '',
        format: 'csv'
      };
    },
    refreshHistory() {
      // 调用API获取导出历史
      this.$message({
        message: '导出历史已刷新',
        type: 'success'
      });
    },
    downloadFile(row) {
      // 调用API下载文件
      this.$message({
        message: `正在下载 ${row.symbol} 的${row.dataType}`,
        type: 'success'
      });
    }
  }
}
</script>

<style scoped>
.data-export-container {
  padding: 20px;
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
