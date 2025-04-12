<template>
  <div class="market-data">
    <!-- Data Overview Section -->
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>数据概览</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="fetchData" icon="el-icon-refresh">刷新</el-button>
      </div>
      <el-table
        v-loading="loadingOverview"
        :data="dataOverview"
        style="width: 100%"
        height="400"
        border>
        <el-table-column
          prop="symbol"
          label="代码"
          width="120"
          sortable>
        </el-table-column>
        <el-table-column
          prop="exchange"
          label="交易所"
          width="100"
          sortable>
        </el-table-column>
        <el-table-column
          prop="interval"
          label="周期"
          width="100"
          sortable>
           <template slot-scope="scope">
            {{ scope.row.interval || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="count"
          label="数据量"
          width="120"
          sortable>
        </el-table-column>
        <el-table-column
          prop="start"
          label="开始时间"
          width="180"
          sortable>
        </el-table-column>
        <el-table-column
          prop="end"
          label="结束时间"
          width="180"
          sortable>
        </el-table-column>
        <el-table-column
          prop="type"
          label="类型"
          width="80"
          :filters="[{ text: 'Bar', value: 'bar' }, { text: 'Tick', value: 'tick' }]"
          :filter-method="filterType"
          filter-placement="bottom-end">
          <template slot-scope="scope">
            <el-tag
              :type="scope.row.type === 'bar' ? 'primary' : 'success'"
              disable-transitions>{{scope.row.type}}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="150"
          fixed="right">
          <template slot-scope="scope">
            <!-- <el-button
              size="mini"
              @click="viewData(scope.row)"
              :disabled="scope.row.type !== 'bar'">查看</el-button> -->
             <el-button
              size="mini"
              type="danger"
              icon="el-icon-delete"
              @click="deleteData(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Import Section -->
    <el-card class="box-card" style="margin-top: 20px;">
       <div slot="header" class="clearfix">
        <span>数据导入</span>
      </div>
      <el-tabs v-model="activeImportTab">
        <el-tab-pane label="CSV 文件导入" name="csv">
          <el-form ref="csvImportForm" :model="csvImportForm" :rules="csvImportRules" label-width="120px" size="small">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="Symbol" prop="symbol">
                  <el-input v-model="csvImportForm.symbol" placeholder="例如：IF2409"></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Exchange" prop="exchange">
                  <el-select v-model="csvImportForm.exchange" placeholder="选择交易所" filterable style="width: 100%;">
                     <!-- Add more exchanges as needed -->
                    <el-option label="CFFEX" value="CFFEX"></el-option>
                    <el-option label="SHFE" value="SHFE"></el-option>
                    <el-option label="DCE" value="DCE"></el-option>
                    <el-option label="CZCE" value="CZCE"></el-option>
                    <el-option label="INE" value="INE"></el-option>
                    <el-option label="SSE" value="SSE"></el-option>
                    <el-option label="SZSE" value="SZSE"></el-option>
                     <el-option label="NASDAQ" value="NASDAQ"></el-option>
                     <el-option label="NYSE" value="NYSE"></el-option>
                    <el-option label="AMEX" value="AMEX"></el-option>
                     <el-option label="HKEX" value="HKEX"></el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Interval" prop="interval">
                   <el-select v-model="csvImportForm.interval" placeholder="选择周期" style="width: 100%;">
                    <el-option label="1分钟" value="1m"></el-option>
                    <el-option label="5分钟" value="5m"></el-option>
                    <el-option label="15分钟" value="15m"></el-option>
                    <el-option label="30分钟" value="30m"></el-option>
                    <el-option label="1小时" value="1h"></el-option>
                    <el-option label="4小时" value="4h"></el-option>
                    <el-option label="日线" value="d"></el-option> <!-- Use 'd' for daily as per vnpy convention -->
                    <el-option label="周线" value="w"></el-option>
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                 <el-form-item label="时间列名" prop="datetime_head">
                   <el-input v-model="csvImportForm.datetime_head" placeholder="例如：datetime, trade_date"></el-input>
                 </el-form-item>
              </el-col>
              <el-col :span="8">
                 <el-form-item label="开盘价列名" prop="open_head">
                   <el-input v-model="csvImportForm.open_head" placeholder="例如：open"></el-input>
                 </el-form-item>
              </el-col>
               <el-col :span="8">
                 <el-form-item label="最高价列名" prop="high_head">
                   <el-input v-model="csvImportForm.high_head" placeholder="例如：high"></el-input>
                 </el-form-item>
              </el-col>
            </el-row>
             <el-row :gutter="20">
               <el-col :span="8">
                 <el-form-item label="最低价列名" prop="low_head">
                   <el-input v-model="csvImportForm.low_head" placeholder="例如：low"></el-input>
                 </el-form-item>
              </el-col>
              <el-col :span="8">
                 <el-form-item label="收盘价列名" prop="close_head">
                   <el-input v-model="csvImportForm.close_head" placeholder="例如：close"></el-input>
                 </el-form-item>
              </el-col>
               <el-col :span="8">
                 <el-form-item label="成交量列名" prop="volume_head">
                   <el-input v-model="csvImportForm.volume_head" placeholder="例如：volume"></el-input>
                 </el-form-item>
              </el-col>
            </el-row>
             <el-row :gutter="20">
                <el-col :span="8">
                 <el-form-item label="持仓量列名" prop="open_interest_head">
                   <el-input v-model="csvImportForm.open_interest_head" placeholder="例如：open_interest"></el-input>
                 </el-form-item>
              </el-col>
              <el-col :span="8">
                 <el-form-item label="时间格式" prop="datetime_format">
                   <el-input v-model="csvImportForm.datetime_format" placeholder="例如：%Y-%m-%d %H:%M:%S"></el-input>
                 </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="选择文件" prop="file">
               <el-upload
                ref="csvUploader"
                :action="uploadUrl" 
                :limit="1"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                :file-list="fileList"
                :auto-upload="false"> 
                <el-button slot="trigger" size="small" type="primary">选取文件</el-button>
                <div slot="tip" class="el-upload__tip">只能上传csv文件</div>
              </el-upload>
            </el-form-item>
             <el-form-item>
                <el-button type="success" @click="submitCsvImport" :loading="loadingCsvImport">开始导入</el-button>
             </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="Qlib 数据导入" name="qlib">
          <!-- Qlib Import Form will go here -->
          <p>Qlib 导入功能待添加...</p>
        </el-tab-pane>
      </el-tabs>
    </el-card>

     <!-- Data Viewing Dialog (Placeholder/Optional) -->
    <!-- <el-dialog title="数据查看" :visible.sync="dataDialogVisible" width="80%">
      <div v-if="currentBarData">
        <div id="kline-chart" style="width: 100%; height: 400px;"></div>
      </div>
    </el-dialog> -->

  </div>
</template>

<script>
import axios from 'axios'; // Using axios for API calls

const API_BASE_URL = 'http://localhost:8000/api/data'; // Backend API base URL

export default {
  name: 'MarketData',
  data() {
    return {
      loadingOverview: false,
      dataOverview: [], // Store overview data
      activeImportTab: 'csv', // Default active tab
      loadingCsvImport: false,
      fileList: [], // For el-upload
      csvImportForm: {
        symbol: '',
        exchange: '',
        interval: 'd', // Default to daily
        datetime_head: 'datetime',
        open_head: 'open',
        high_head: 'high',
        low_head: 'low',
        close_head: 'close',
        volume_head: 'volume',
        open_interest_head: 'open_interest',
        datetime_format: '%Y-%m-%d %H:%M:%S', // Default format
        file: null // Store the File object
      },
      csvImportRules: {
        symbol: [{ required: true, message: '请输入Symbol', trigger: 'blur' }],
        exchange: [{ required: true, message: '请选择Exchange', trigger: 'change' }],
        interval: [{ required: true, message: '请选择Interval', trigger: 'change' }],
        datetime_head: [{ required: true, message: '请输入时间列名', trigger: 'blur' }],
        open_head: [{ required: true, message: '请输入开盘价列名', trigger: 'blur' }],
        high_head: [{ required: true, message: '请输入最高价列名', trigger: 'blur' }],
        low_head: [{ required: true, message: '请输入最低价列名', trigger: 'blur' }],
        close_head: [{ required: true, message: '请输入收盘价列名', trigger: 'blur' }],
        volume_head: [{ required: true, message: '请输入成交量列名', trigger: 'blur' }],
        open_interest_head: [{ required: true, message: '请输入持仓量列名', trigger: 'blur' }],
        datetime_format: [{ required: true, message: '请输入时间格式', trigger: 'blur' }],
        file: [{ required: true, message: '请选择要上传的CSV文件', trigger: 'change' }]
      },
      uploadUrl: '' // Dummy URL for el-upload action
      // dataDialogVisible: false,
      // currentBarData: null, // Store data for viewing
    };
  },
  methods: {
    // Fetch data overview from backend
    async fetchData() {
      this.loadingOverview = true;
      try {
        const response = await axios.get(`${API_BASE_URL}/overview`);
        if (response.data && response.data.success) {
          this.dataOverview = response.data.data;
          this.$message.success('数据概览已更新');
        } else {
          this.$message.error('获取数据概览失败: ' + (response.data.message || '未知错误'));
          this.dataOverview = []; // Clear data on error
        }
      } catch (error) {
        console.error("Error fetching data overview:", error);
        this.$message.error('获取数据概览请求失败: ' + (error.response?.data?.detail || error.message));
        this.dataOverview = []; // Clear data on error
      } finally {
        this.loadingOverview = false;
      }
    },

    // Delete data
    deleteData(row) {
      const type = row.type;
      const { exchange, symbol, interval } = row;
      const confirmMessage = `确定删除 ${symbol}.${exchange} (${interval || 'TICK'}) 的数据吗? 数据删除后不可恢复！`;
      const deleteUrl = type === 'bar'
        ? `${API_BASE_URL}/bar/${exchange}/${symbol}/${interval}`
        : `${API_BASE_URL}/tick/${exchange}/${symbol}`;

      this.$confirm(confirmMessage, '警告', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        this.loadingOverview = true; // Show loading on table while deleting
        try {
          const response = await axios.delete(deleteUrl);
          if (response.data && response.data.success) {
            this.$message({
              type: 'success',
              message: '删除成功!'
            });
            // Refresh data overview after successful deletion
            await this.fetchData();
          } else {
            this.$message({
              type: 'error',
              message: '删除失败: ' + (response.data.message || '未知错误')
            });
          }
        } catch (error) {
           console.error("Error deleting data:", error);
           this.$message({
            type: 'error',
            message: '删除操作失败: ' + (error.response?.data?.detail || error.message)
          });
        } finally {
           this.loadingOverview = false;
        }
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });
    },

    // Filter table by data type
    filterType(value, row) {
        return row.type === value;
    },

    // Placeholder for viewing data (optional, needs kline chart integration)
    // async viewData(row) {
    //   if (row.type !== 'bar') {
    //       this.$message.warning('目前仅支持查看K线数据');
    //       return;
    //   }
    //   // Logic to fetch bar data for the selected row
    //   // ... fetch data using GET /api/data/bars ...
    //   // this.currentBarData = fetchedData;
    //   // this.dataDialogVisible = true;
    //   // this.$nextTick(() => { this.renderKlineChart(); });
    // },
    // renderKlineChart() {
    //    // Logic to render echarts kline chart
    // }

    // ---- CSV Import Methods ----
    handleFileChange(file, fileList) {
        // Validate file type (optional, can also rely on accept attribute)
        const isCSV = file.raw.type === 'text/csv' || file.name.toLowerCase().endsWith('.csv');
        if (!isCSV) {
            this.$message.error('只能上传 CSV 格式的文件!');
            // Remove the invalid file
            this.$refs.csvUploader.clearFiles();
            this.csvImportForm.file = null;
            this.fileList = [];
            return false;
        }
        // Store the file object for later submission
        this.csvImportForm.file = file.raw; 
        // Keep only the last selected file in the list for display
        this.fileList = fileList.slice(-1);
        // Manually trigger validation after file selection
        this.$refs.csvImportForm.validateField('file');
    },

    handleFileRemove(file, fileList) {
        this.csvImportForm.file = null;
        this.fileList = [];
        // Manually trigger validation after file removal
         this.$refs.csvImportForm.validateField('file');
    },

    submitCsvImport() {
      this.$refs.csvImportForm.validate(async (valid) => {
        if (valid) {
          this.loadingCsvImport = true;
          const formData = new FormData();
          
          // Append file
          formData.append('file', this.csvImportForm.file);

          // Append other form parameters
          Object.keys(this.csvImportForm).forEach(key => {
            if (key !== 'file') { // Don't append the file object itself again
              formData.append(key, this.csvImportForm[key]);
            }
          });

          try {
            const response = await axios.post(`${API_BASE_URL}/import/csv`, formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });

            if (response.data && response.data.success) {
              this.$message.success('CSV文件导入成功: ' + response.data.message);
              // Clear the form and file list
              this.$refs.csvImportForm.resetFields();
              this.$refs.csvUploader.clearFiles(); 
              this.csvImportForm.file = null;
              this.fileList = [];
              // Refresh overview data
              await this.fetchData();
            } else {
              this.$message.error('CSV文件导入失败: ' + (response.data.message || '未知错误'));
            }
          } catch (error) {
            console.error("Error importing CSV:", error);
            this.$message.error('CSV文件导入请求失败: ' + (error.response?.data?.detail || error.message));
          } finally {
            this.loadingCsvImport = false;
          }
        } else {
          console.log('CSV import form validation failed');
          return false;
        }
      });
    },
    // ---- End CSV Import Methods ----

  },
  mounted() {
    // Fetch initial data when component is mounted
    this.fetchData();
  }
};
</script>

<style scoped>
.market-data {
  padding: 20px;
}
.box-card {
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