<template>
  <div class="orders-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>订单管理</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="refreshOrders">刷新</el-button>
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
        
        <el-form-item label="订单状态">
          <el-select v-model="filterForm.status" placeholder="请选择订单状态" clearable>
            <el-option label="未成交" value="SUBMITTING"></el-option>
            <el-option label="部分成交" value="PARTTRADED"></el-option>
            <el-option label="全部成交" value="ALLTRADED"></el-option>
            <el-option label="已撤销" value="CANCELLED"></el-option>
            <el-option label="拒单" value="REJECTED"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="yyyy-MM-dd"
            value-format="yyyy-MM-dd">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="filterOrders">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="活动订单" name="active"></el-tab-pane>
        <el-tab-pane label="历史订单" name="history"></el-tab-pane>
      </el-tabs>
      
      <el-table
        :data="ordersData"
        style="width: 100%"
        border
        v-loading="loading">
        <el-table-column prop="orderid" label="订单编号" width="120"></el-table-column>
        <el-table-column prop="symbol" label="合约代码" width="120"></el-table-column>
        <el-table-column prop="exchange" label="交易所" width="100"></el-table-column>
        <el-table-column prop="direction" label="方向" width="80">
          <template slot-scope="scope">
            <el-tag :type="scope.row.direction === 'LONG' ? 'danger' : 'success'">
              {{ scope.row.direction === 'LONG' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="offset" label="开平" width="80">
          <template slot-scope="scope">
            <el-tag :type="scope.row.offset === 'OPEN' ? 'primary' : 'warning'">
              {{ 
                scope.row.offset === 'OPEN' ? '开仓' : 
                scope.row.offset === 'CLOSE' ? '平仓' : 
                scope.row.offset === 'CLOSETODAY' ? '平今' : '平昨'
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="100"></el-table-column>
        <el-table-column prop="volume" label="总数量" width="80"></el-table-column>
        <el-table-column prop="traded" label="已成交" width="80"></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="orderTime" label="委托时间" width="180"></el-table-column>
        <el-table-column prop="cancelTime" label="撤销时间" width="180"></el-table-column>
        <el-table-column prop="gateway" label="接口" width="100"></el-table-column>
        <el-table-column label="操作" fixed="right" width="120">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="danger"
              :disabled="!canCancel(scope.row.status)"
              @click="handleCancel(scope.row)">撤单</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total">
        </el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'TradingOrders',
  data() {
    return {
      loading: false,
      activeTab: 'active',
      filterForm: {
        gateway: '',
        exchange: '',
        symbol: '',
        status: '',
        dateRange: []
      },
      ordersData: [
        {
          orderid: '2024041300001',
          symbol: '600000',
          exchange: 'SSE',
          direction: 'LONG',
          offset: 'OPEN',
          price: 10.25,
          volume: 1000,
          traded: 1000,
          status: 'ALLTRADED',
          orderTime: '2024-04-13 09:30:15',
          cancelTime: '',
          gateway: 'tiger'
        },
        {
          orderid: '2024041300002',
          symbol: '000001',
          exchange: 'SZSE',
          direction: 'SHORT',
          offset: 'CLOSE',
          price: 15.75,
          volume: 500,
          traded: 0,
          status: 'CANCELLED',
          orderTime: '2024-04-13 10:15:30',
          cancelTime: '2024-04-13 10:16:45',
          gateway: 'ib'
        },
        {
          orderid: '2024041300003',
          symbol: 'IF2106',
          exchange: 'CFFEX',
          direction: 'LONG',
          offset: 'OPEN',
          price: 5320.00,
          volume: 2,
          traded: 1,
          status: 'PARTTRADED',
          orderTime: '2024-04-13 11:05:22',
          cancelTime: '',
          gateway: 'ctp'
        },
        {
          orderid: '2024041300004',
          symbol: '600519',
          exchange: 'SSE',
          direction: 'LONG',
          offset: 'OPEN',
          price: 1800.50,
          volume: 100,
          traded: 0,
          status: 'SUBMITTING',
          orderTime: '2024-04-13 13:30:45',
          cancelTime: '',
          gateway: 'tiger'
        }
      ],
      currentPage: 1,
      pageSize: 10,
      total: 4
    }
  },
  methods: {
    refreshOrders() {
      this.loading = true;
      
      // 模拟API请求
      setTimeout(() => {
        this.loading = false;
        this.$message.success('订单数据已刷新');
      }, 1000);
    },
    filterOrders() {
      this.loading = true;
      
      // 模拟API请求
      setTimeout(() => {
        // 过滤数据
        const filteredData = this.ordersData.filter(order => {
          let match = true;
          if (this.filterForm.gateway && order.gateway !== this.filterForm.gateway) {
            match = false;
          }
          if (this.filterForm.exchange && order.exchange !== this.filterForm.exchange) {
            match = false;
          }
          if (this.filterForm.symbol && !order.symbol.includes(this.filterForm.symbol)) {
            match = false;
          }
          if (this.filterForm.status && order.status !== this.filterForm.status) {
            match = false;
          }
          // 日期范围过滤
          if (this.filterForm.dateRange && this.filterForm.dateRange.length === 2) {
            const orderDate = order.orderTime.split(' ')[0];
            if (orderDate < this.filterForm.dateRange[0] || orderDate > this.filterForm.dateRange[1]) {
              match = false;
            }
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
        symbol: '',
        status: '',
        dateRange: []
      };
      this.filterOrders();
    },
    handleTabClick(tab) {
      if (tab.name === 'active') {
        // 加载活动订单
        this.ordersData = this.ordersData.filter(order => 
          order.status === 'SUBMITTING' || order.status === 'PARTTRADED'
        );
      } else {
        // 加载历史订单
        this.ordersData = this.ordersData.filter(order => 
          order.status === 'ALLTRADED' || order.status === 'CANCELLED' || order.status === 'REJECTED'
        );
      }
    },
    getStatusType(status) {
      switch (status) {
        case 'SUBMITTING':
          return 'info';
        case 'PARTTRADED':
          return 'warning';
        case 'ALLTRADED':
          return 'success';
        case 'CANCELLED':
          return '';
        case 'REJECTED':
          return 'danger';
        default:
          return '';
      }
    },
    getStatusText(status) {
      switch (status) {
        case 'SUBMITTING':
          return '未成交';
        case 'PARTTRADED':
          return '部分成交';
        case 'ALLTRADED':
          return '全部成交';
        case 'CANCELLED':
          return '已撤销';
        case 'REJECTED':
          return '拒单';
        default:
          return status;
      }
    },
    canCancel(status) {
      return status === 'SUBMITTING' || status === 'PARTTRADED';
    },
    handleCancel(row) {
      this.$confirm(`确定要撤销订单 ${row.orderid} 吗?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 调用API撤销订单
        this.$message.success(`订单 ${row.orderid} 撤销请求已提交`);
        
        // 模拟撤单成功
        setTimeout(() => {
          const index = this.ordersData.findIndex(item => item.orderid === row.orderid);
          if (index !== -1) {
            this.ordersData[index].status = 'CANCELLED';
            this.ordersData[index].cancelTime = new Date().toLocaleString();
            this.$message.success(`订单 ${row.orderid} 已成功撤销`);
          }
        }, 1000);
      }).catch(() => {
        this.$message.info('已取消撤单操作');
      });
    },
    handleSizeChange(val) {
      this.pageSize = val;
      this.filterOrders();
    },
    handleCurrentChange(val) {
      this.currentPage = val;
      this.filterOrders();
    }
  },
  created() {
    this.refreshOrders();
  }
}
</script>

<style scoped>
.orders-container {
  padding: 20px;
}
.filter-form {
  margin-bottom: 20px;
}
.pagination-container {
  margin-top: 20px;
  text-align: right;
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
