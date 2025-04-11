<template>
  <div class="positions-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>持仓管理</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="refreshPositions">刷新</el-button>
      </div>
      
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="交易接口">
          <el-select v-model="filterForm.gateway" placeholder="请选择交易接口" clearable>
            <el-option label="老虎证券" value="tiger"></el-option>
            <el-option label="盈透证券" value="ib"></el-option>
            <el-option label="CTP" value="ctp"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="交易所">
          <el-select v-model="filterForm.exchange" placeholder="请选择交易所" clearable>
            <el-option label="上海证券交易所" value="SSE"></el-option>
            <el-option label="深圳证券交易所" value="SZSE"></el-option>
            <el-option label="中国金融期货交易所" value="CFFEX"></el-option>
            <el-option label="上海期货交易所" value="SHFE"></el-option>
            <el-option label="大连商品交易所" value="DCE"></el-option>
            <el-option label="郑州商品交易所" value="CZCE"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="合约代码">
          <el-input v-model="filterForm.symbol" placeholder="请输入合约代码" clearable></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="filterPositions">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table
        :data="positionsData"
        style="width: 100%"
        border
        v-loading="loading"
        :row-class-name="getRowClassName">
        <el-table-column prop="symbol" label="合约代码" width="120"></el-table-column>
        <el-table-column prop="exchange" label="交易所" width="120"></el-table-column>
        <el-table-column prop="direction" label="方向" width="80">
          <template slot-scope="scope">
            <el-tag :type="scope.row.direction === 'LONG' ? 'danger' : 'success'">
              {{ scope.row.direction === 'LONG' ? '多' : '空' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="持仓量" width="100"></el-table-column>
        <el-table-column prop="frozen" label="冻结量" width="100"></el-table-column>
        <el-table-column prop="price" label="持仓均价" width="120"></el-table-column>
        <el-table-column prop="pnl" label="持仓盈亏" width="120">
          <template slot-scope="scope">
            <span :class="scope.row.pnl >= 0 ? 'profit' : 'loss'">
              {{ scope.row.pnl }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="pnlRatio" label="盈亏比例" width="120">
          <template slot-scope="scope">
            <span :class="scope.row.pnlRatio >= 0 ? 'profit' : 'loss'">
              {{ scope.row.pnlRatio }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="ydVolume" label="昨仓" width="100"></el-table-column>
        <el-table-column prop="tdVolume" label="今仓" width="100"></el-table-column>
        <el-table-column prop="gateway" label="接口" width="120"></el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              @click="handleClose(scope.row)">平仓</el-button>
            <el-button
              size="mini"
              type="warning"
              @click="handleModify(scope.row)">修改止损</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="position-summary">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="summary-item">
              <span class="label">总持仓市值:</span>
              <span class="value">{{ totalValue }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-item">
              <span class="label">总持仓盈亏:</span>
              <span :class="['value', totalPnl >= 0 ? 'profit' : 'loss']">{{ totalPnl }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-item">
              <span class="label">总盈亏比例:</span>
              <span :class="['value', totalPnlRatio >= 0 ? 'profit' : 'loss']">{{ totalPnlRatio }}%</span>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
    
    <!-- 平仓对话框 -->
    <el-dialog title="平仓" :visible.sync="closeDialogVisible" width="30%">
      <el-form :model="closeForm" label-width="100px">
        <el-form-item label="合约代码">
          <span>{{ closeForm.symbol }}</span>
        </el-form-item>
        <el-form-item label="方向">
          <span>{{ closeForm.direction === 'LONG' ? '多' : '空' }}</span>
        </el-form-item>
        <el-form-item label="持仓量">
          <span>{{ closeForm.volume }}</span>
        </el-form-item>
        <el-form-item label="平仓数量">
          <el-input-number v-model="closeForm.closeVolume" :min="1" :max="closeForm.volume" :step="1"></el-input-number>
        </el-form-item>
        <el-form-item label="价格类型">
          <el-select v-model="closeForm.orderType" placeholder="请选择价格类型">
            <el-option label="限价单" value="LIMIT"></el-option>
            <el-option label="市价单" value="MARKET"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="价格" v-if="closeForm.orderType === 'LIMIT'">
          <el-input-number v-model="closeForm.price" :precision="2" :step="0.01" :min="0"></el-input-number>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="closeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitClose">确定</el-button>
      </span>
    </el-dialog>
    
    <!-- 修改止损对话框 -->
    <el-dialog title="修改止损" :visible.sync="stopLossDialogVisible" width="30%">
      <el-form :model="stopLossForm" label-width="100px">
        <el-form-item label="合约代码">
          <span>{{ stopLossForm.symbol }}</span>
        </el-form-item>
        <el-form-item label="方向">
          <span>{{ stopLossForm.direction === 'LONG' ? '多' : '空' }}</span>
        </el-form-item>
        <el-form-item label="持仓均价">
          <span>{{ stopLossForm.price }}</span>
        </el-form-item>
        <el-form-item label="止损价格">
          <el-input-number v-model="stopLossForm.stopLossPrice" :precision="2" :step="0.01" :min="0"></el-input-number>
        </el-form-item>
        <el-form-item label="止盈价格">
          <el-input-number v-model="stopLossForm.takeProfitPrice" :precision="2" :step="0.01" :min="0"></el-input-number>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="stopLossDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStopLoss">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'TradingPositions',
  data() {
    return {
      loading: false,
      filterForm: {
        gateway: '',
        exchange: '',
        symbol: ''
      },
      positionsData: [
        {
          symbol: '600000',
          exchange: 'SSE',
          direction: 'LONG',
          volume: 1000,
          frozen: 0,
          price: 10.25,
          pnl: 250.00,
          pnlRatio: 2.44,
          ydVolume: 1000,
          tdVolume: 0,
          gateway: 'tiger'
        },
        {
          symbol: '000001',
          exchange: 'SZSE',
          direction: 'SHORT',
          volume: 500,
          frozen: 0,
          price: 15.75,
          pnl: -125.00,
          pnlRatio: -1.59,
          ydVolume: 300,
          tdVolume: 200,
          gateway: 'ib'
        },
        {
          symbol: 'IF2106',
          exchange: 'CFFEX',
          direction: 'LONG',
          volume: 2,
          frozen: 0,
          price: 5320.00,
          pnl: 1200.00,
          pnlRatio: 11.28,
          ydVolume: 0,
          tdVolume: 2,
          gateway: 'ctp'
        }
      ],
      closeDialogVisible: false,
      closeForm: {
        symbol: '',
        direction: '',
        volume: 0,
        closeVolume: 0,
        orderType: 'LIMIT',
        price: 0
      },
      stopLossDialogVisible: false,
      stopLossForm: {
        symbol: '',
        direction: '',
        price: 0,
        stopLossPrice: 0,
        takeProfitPrice: 0
      }
    }
  },
  computed: {
    totalValue() {
      let total = 0;
      this.positionsData.forEach(position => {
        total += position.volume * position.price;
      });
      return total.toFixed(2);
    },
    totalPnl() {
      let total = 0;
      this.positionsData.forEach(position => {
        total += position.pnl;
      });
      return total.toFixed(2);
    },
    totalPnlRatio() {
      if (this.totalValue === 0) return 0;
      return ((this.totalPnl / this.totalValue) * 100).toFixed(2);
    }
  },
  methods: {
    refreshPositions() {
      this.loading = true;
      
      // 模拟API请求
      setTimeout(() => {
        this.loading = false;
        this.$message.success('持仓数据已刷新');
      }, 1000);
    },
    filterPositions() {
      this.loading = true;
      
      // 模拟API请求
      setTimeout(() => {
        // 过滤数据
        const filteredData = this.positionsData.filter(position => {
          let match = true;
          if (this.filterForm.gateway && position.gateway !== this.filterForm.gateway) {
            match = false;
          }
          if (this.filterForm.exchange && position.exchange !== this.filterForm.exchange) {
            match = false;
          }
          if (this.filterForm.symbol && !position.symbol.includes(this.filterForm.symbol)) {
            match = false;
          }
          return match;
        });
        
        this.loading = false;
        this.$message.success('查询成功');
      }, 500);
    },
    resetFilter() {
      this.filterForm = {
        gateway: '',
        exchange: '',
        symbol: ''
      };
      this.filterPositions();
    },
    getRowClassName({ row }) {
      if (row.pnl >= 0) {
        return 'profit-row';
      } else {
        return 'loss-row';
      }
    },
    handleClose(row) {
      this.closeForm = {
        symbol: row.symbol,
        direction: row.direction,
        volume: row.volume,
        closeVolume: row.volume,
        orderType: 'LIMIT',
        price: row.price
      };
      this.closeDialogVisible = true;
    },
    handleModify(row) {
      this.stopLossForm = {
        symbol: row.symbol,
        direction: row.direction,
        price: row.price,
        stopLossPrice: row.direction === 'LONG' ? row.price * 0.95 : row.price * 1.05,
        takeProfitPrice: row.direction === 'LONG' ? row.price * 1.1 : row.price * 0.9
      };
      this.stopLossDialogVisible = true;
    },
    submitClose() {
      // 调用API提交平仓订单
      this.$message.success(`已提交平仓订单: ${this.closeForm.symbol} ${this.closeForm.closeVolume}手`);
      this.closeDialogVisible = false;
    },
    submitStopLoss() {
      // 调用API设置止损止盈
      this.$message.success(`已设置止损止盈: ${this.stopLossForm.symbol}`);
      this.stopLossDialogVisible = false;
    }
  },
  created() {
    this.refreshPositions();
  }
}
</script>

<style scoped>
.positions-container {
  padding: 20px;
}
.filter-form {
  margin-bottom: 20px;
}
.position-summary {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.label {
  font-weight: bold;
  color: #606266;
}
.value {
  font-size: 16px;
  font-weight: bold;
}
.profit {
  color: #f56c6c;
}
.loss {
  color: #67c23a;
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

<style>
.profit-row {
  background-color: rgba(245, 108, 108, 0.1);
}
.loss-row {
  background-color: rgba(103, 194, 58, 0.1);
}
</style>
