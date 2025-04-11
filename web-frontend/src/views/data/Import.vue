<template>
  <div class="data-import-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>数据导入</span>
      </div>
      <el-form :model="importForm" label-width="100px">
        <el-form-item label="数据类型">
          <el-select v-model="importForm.dataType" placeholder="请选择数据类型">
            <el-option label="K线数据" value="kline"></el-option>
            <el-option label="Tick数据" value="tick"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="交易所">
          <el-select v-model="importForm.exchange" placeholder="请选择交易所">
            <el-option label="上海证券交易所" value="SSE"></el-option>
            <el-option label="深圳证券交易所" value="SZSE"></el-option>
            <el-option label="中国金融期货交易所" value="CFFEX"></el-option>
            <el-option label="上海期货交易所" value="SHFE"></el-option>
            <el-option label="大连商品交易所" value="DCE"></el-option>
            <el-option label="郑州商品交易所" value="CZCE"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="合约代码">
          <el-input v-model="importForm.symbol" placeholder="请输入合约代码"></el-input>
        </el-form-item>
        
        <el-form-item label="时间周期" v-if="importForm.dataType === 'kline'">
          <el-select v-model="importForm.interval" placeholder="请选择时间周期">
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
            v-model="importForm.startDate"
            type="date"
            placeholder="选择开始日期"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="importForm.endDate"
            type="date"
            placeholder="选择结束日期"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="数据文件">
          <el-upload
            class="upload-demo"
            action="/api/data/upload"
            :on-preview="handlePreview"
            :on-remove="handleRemove"
            :before-remove="beforeRemove"
            :on-success="handleSuccess"
            :on-error="handleError"
            :file-list="fileList">
            <el-button size="small" type="primary">点击上传</el-button>
            <div slot="tip" class="el-upload__tip">只能上传CSV文件，且不超过10MB</div>
          </el-upload>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitImport">导入数据</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'DataImport',
  data() {
    return {
      importForm: {
        dataType: 'kline',
        exchange: '',
        symbol: '',
        interval: '1d',
        startDate: '',
        endDate: ''
      },
      fileList: []
    }
  },
  methods: {
    submitImport() {
      // 调用API导入数据
      this.$message({
        message: '数据导入请求已提交，请等待处理',
        type: 'success'
      });
    },
    resetForm() {
      this.importForm = {
        dataType: 'kline',
        exchange: '',
        symbol: '',
        interval: '1d',
        startDate: '',
        endDate: ''
      };
      this.fileList = [];
    },
    handleRemove(file, fileList) {
      console.log(file, fileList);
    },
    handlePreview(file) {
      console.log(file);
    },
    beforeRemove(file) {
      return this.$confirm(`确定移除 ${file.name}？`);
    },
    handleSuccess(response, file, fileList) {
      this.$message({
        message: '文件上传成功',
        type: 'success'
      });
    },
    handleError(err, file, fileList) {
      this.$message.error('文件上传失败');
    }
  }
}
</script>

<style scoped>
.data-import-container {
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
