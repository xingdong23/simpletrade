<template>
  <div>
    <!-- 顶部标签导航 -->
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="账户概览" name="overview">
        <div style="margin-bottom: 20px;">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card shadow="hover">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">账户总资产</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #303133; margin: 0;">¥ 1,250,000</p>
                  <div style="margin-top: 10px; font-size: 14px; color: #67C23A;">
                    <i class="el-icon-top"></i> +2.5% 今日
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card shadow="hover">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">可用资金</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #303133; margin: 0;">¥ 450,000</p>
                  <div style="margin-top: 10px; font-size: 14px; color: #909399;">
                    36% 总资产
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card shadow="hover">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">持仓市值</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #303133; margin: 0;">¥ 800,000</p>
                  <div style="margin-top: 10px; font-size: 14px; color: #909399;">
                    64% 总资产
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card shadow="hover">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">今日盈亏</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #67C23A; margin: 0;">¥ 32,500</p>
                  <div style="margin-top: 10px; font-size: 14px; color: #67C23A;">
                    <i class="el-icon-top"></i> +2.5% 今日
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <!-- 资产走势图 -->
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <div slot="header">
            <span>资产走势</span>
            <el-radio-group v-model="timeRange" size="small" style="float: right;">
              <el-radio-button label="week">周</el-radio-button>
              <el-radio-button label="month">月</el-radio-button>
              <el-radio-button label="year">年</el-radio-button>
            </el-radio-group>
          </div>
          <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: #909399;">
            <i class="el-icon-data-analysis" style="font-size: 24px; margin-right: 10px;"></i>
            资产走势图（这里将显示图表）
          </div>
        </el-card>
        
        <!-- 最近交易 -->
        <el-card shadow="hover">
          <div slot="header">
            <span>最近交易</span>
            <el-button style="float: right;" type="text">查看全部</el-button>
          </div>
          <el-table :data="recentTrades" style="width: 100%">
            <el-table-column prop="time" label="时间" width="180"></el-table-column>
            <el-table-column prop="symbol" label="股票代码" width="120"></el-table-column>
            <el-table-column prop="name" label="股票名称" width="150"></el-table-column>
            <el-table-column prop="type" label="交易类型" width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.type === '买入' ? 'success' : 'danger'" size="small">{{ scope.row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="120"></el-table-column>
            <el-table-column prop="quantity" label="数量" width="120"></el-table-column>
            <el-table-column prop="amount" label="金额"></el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="持仓" name="positions">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">持仓列表</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-input
                placeholder="搜索股票..."
                prefix-icon="el-icon-search"
                style="width: 200px;"
              ></el-input>
            </el-col>
          </el-row>
        </div>
        
        <el-table :data="positions" style="width: 100%" border>
          <el-table-column prop="symbol" label="股票代码" width="120"></el-table-column>
          <el-table-column prop="name" label="股票名称" width="150"></el-table-column>
          <el-table-column prop="quantity" label="持仓数量" width="120"></el-table-column>
          <el-table-column prop="costPrice" label="成本价" width="120"></el-table-column>
          <el-table-column prop="currentPrice" label="当前价" width="120"></el-table-column>
          <el-table-column prop="marketValue" label="市值" width="150"></el-table-column>
          <el-table-column prop="profit" label="盈亏" width="120">
            <template slot-scope="scope">
              <span :style="{ color: scope.row.profit >= 0 ? '#67C23A' : '#F56C6C' }">
                {{ scope.row.profit >= 0 ? '+' : '' }}{{ scope.row.profit }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="profitPercent" label="盈亏比例" width="120">
            <template slot-scope="scope">
              <span :style="{ color: scope.row.profitPercent >= 0 ? '#67C23A' : '#F56C6C' }">
                {{ scope.row.profitPercent >= 0 ? '+' : '' }}{{ scope.row.profitPercent }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template slot-scope="scope">
              <el-button size="mini" type="primary" @click="handleBuy(scope.row)">买入</el-button>
              <el-button size="mini" type="danger" @click="handleSell(scope.row)">卖出</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <el-tab-pane label="订单" name="orders">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">订单列表</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-radio-group v-model="orderStatus" size="small">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="pending">待成交</el-radio-button>
                <el-radio-button label="completed">已成交</el-radio-button>
                <el-radio-button label="canceled">已撤销</el-radio-button>
              </el-radio-group>
            </el-col>
          </el-row>
        </div>
        
        <el-table :data="orders" style="width: 100%" border>
          <el-table-column prop="time" label="时间" width="180"></el-table-column>
          <el-table-column prop="symbol" label="股票代码" width="120"></el-table-column>
          <el-table-column prop="name" label="股票名称" width="150"></el-table-column>
          <el-table-column prop="type" label="交易类型" width="100">
            <template slot-scope="scope">
              <el-tag :type="scope.row.type === '买入' ? 'success' : 'danger'" size="small">{{ scope.row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格" width="120"></el-table-column>
          <el-table-column prop="quantity" label="数量" width="120"></el-table-column>
          <el-table-column prop="amount" label="金额" width="150"></el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template slot-scope="scope">
              <el-tag 
                :type="scope.row.status === '已成交' ? 'success' : scope.row.status === '待成交' ? 'warning' : 'info'" 
                size="small"
              >
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template slot-scope="scope">
              <el-button 
                size="mini" 
                type="text" 
                @click="handleCancelOrder(scope.row)"
                :disabled="scope.row.status !== '待成交'"
              >
                撤销
              </el-button>
              <el-button size="mini" type="text" @click="handleViewOrder(scope.row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
export default {
  name: 'TradingCenterView',
  data() {
    return {
      activeTab: 'overview',
      timeRange: 'month',
      orderStatus: 'all',
      recentTrades: [
        {
          time: '2023-10-15 14:30:25',
          symbol: '600000',
          name: '浦发银行',
          type: '买入',
          price: '10.25',
          quantity: '1000',
          amount: '10,250.00'
        },
        {
          time: '2023-10-15 11:20:15',
          symbol: '000001',
          name: '平安银行',
          type: '卖出',
          price: '15.80',
          quantity: '500',
          amount: '7,900.00'
        },
        {
          time: '2023-10-14 15:45:30',
          symbol: '601318',
          name: '中国平安',
          type: '买入',
          price: '42.50',
          quantity: '200',
          amount: '8,500.00'
        }
      ],
      positions: [
        {
          symbol: '600000',
          name: '浦发银行',
          quantity: '1000',
          costPrice: '10.25',
          currentPrice: '10.50',
          marketValue: '10,500.00',
          profit: '250.00',
          profitPercent: 2.44
        },
        {
          symbol: '601318',
          name: '中国平安',
          quantity: '200',
          costPrice: '42.50',
          currentPrice: '41.80',
          marketValue: '8,360.00',
          profit: '-140.00',
          profitPercent: -1.65
        },
        {
          symbol: '000651',
          name: '格力电器',
          quantity: '300',
          costPrice: '35.20',
          currentPrice: '36.50',
          marketValue: '10,950.00',
          profit: '390.00',
          profitPercent: 3.69
        }
      ],
      orders: [
        {
          time: '2023-10-15 14:30:25',
          symbol: '600000',
          name: '浦发银行',
          type: '买入',
          price: '10.25',
          quantity: '1000',
          amount: '10,250.00',
          status: '已成交'
        },
        {
          time: '2023-10-15 11:20:15',
          symbol: '000001',
          name: '平安银行',
          type: '卖出',
          price: '15.80',
          quantity: '500',
          amount: '7,900.00',
          status: '已成交'
        },
        {
          time: '2023-10-15 10:05:40',
          symbol: '601988',
          name: '中国银行',
          type: '买入',
          price: '3.50',
          quantity: '2000',
          amount: '7,000.00',
          status: '待成交'
        }
      ]
    }
  },
  methods: {
    handleBuy(row) {
      console.log('买入:', row);
    },
    handleSell(row) {
      console.log('卖出:', row);
    },
    handleCancelOrder(row) {
      console.log('撤销订单:', row);
    },
    handleViewOrder(row) {
      console.log('查看订单详情:', row);
    }
  }
}
</script>

<style>
.el-tabs__header {
  margin-bottom: 25px;
}
</style>
