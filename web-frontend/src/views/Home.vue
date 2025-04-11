<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <div class="welcome-header">
            <h2>欢迎使用 SimpleTrade 量化交易平台</h2>
            <p>一个简单易用的个人量化交易平台，支持策略交易、数据分析和实时监控</p>
          </div>
          <el-divider></el-divider>
          <div class="system-status">
            <h3>系统状态</h3>
            <el-row :gutter="20">
              <el-col :span="8" v-for="(item, index) in statusItems" :key="index">
                <div class="status-item">
                  <div class="status-icon">
                    <i :class="item.icon"></i>
                  </div>
                  <div class="status-info">
                    <div class="status-title">{{ item.title }}</div>
                    <div class="status-value">
                      <el-tag :type="item.status ? 'success' : 'danger'">
                        {{ item.status ? '正常' : '异常' }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card class="feature-card">
          <div slot="header" class="clearfix">
            <span>数据管理</span>
          </div>
          <div class="feature-content">
            <div class="feature-icon">
              <i class="el-icon-s-data"></i>
            </div>
            <div class="feature-description">
              <p>管理您的交易数据，包括导入、导出和查询功能。</p>
            </div>
            <el-button type="primary" @click="$router.push('/data')">开始使用</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card">
          <div slot="header" class="clearfix">
            <span>数据分析</span>
          </div>
          <div class="feature-content">
            <div class="feature-icon">
              <i class="el-icon-s-marketing"></i>
            </div>
            <div class="feature-description">
              <p>使用技术指标分析您的交易数据，发现市场趋势。</p>
            </div>
            <el-button type="primary" @click="$router.push('/analysis')">开始分析</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card">
          <div slot="header" class="clearfix">
            <span>交易中心</span>
          </div>
          <div class="feature-content">
            <div class="feature-icon">
              <i class="el-icon-s-finance"></i>
            </div>
            <div class="feature-description">
              <p>连接交易接口，进行实时交易和持仓管理。</p>
            </div>
            <el-button type="primary" @click="$router.push('/trading')">开始交易</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card class="feature-card">
          <div slot="header" class="clearfix">
            <span>策略管理</span>
          </div>
          <div class="feature-content">
            <div class="feature-icon">
              <i class="el-icon-notebook-1"></i>
            </div>
            <div class="feature-description">
              <p>创建、管理和配置您的交易策略。</p>
            </div>
            <el-button type="primary" @click="$router.push('/strategy')">管理策略</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card">
          <div slot="header" class="clearfix">
            <span>回测系统</span>
          </div>
          <div class="feature-content">
            <div class="feature-icon">
              <i class="el-icon-pie-chart"></i>
            </div>
            <div class="feature-description">
              <p>对您的交易策略进行历史数据回测和性能评估。</p>
            </div>
            <el-button type="primary" @click="$router.push('/backtest')">开始回测</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card">
          <div slot="header" class="clearfix">
            <span>AI分析</span>
          </div>
          <div class="feature-content">
            <div class="feature-icon">
              <i class="el-icon-cpu"></i>
            </div>
            <div class="feature-description">
              <p>利用AI模型进行市场预测和策略优化。</p>
            </div>
            <el-button type="primary" @click="$router.push('/ai')">AI分析</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
         <el-card class="feature-card">
           <div slot="header" class="clearfix">
             <span>系统设置</span>
           </div>
           <div class="feature-content">
             <div class="feature-icon">
               <i class="el-icon-setting"></i>
             </div>
             <div class="feature-description">
               <p>配置系统参数、交易接口和通知设置。</p>
             </div>
             <el-button type="primary" @click="$router.push('/settings')">系统设置</el-button>
           </div>
         </el-card>
       </el-col>
       </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>市场概览</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="refreshMarketInfo">刷新</el-button>
          </div>
          <div v-loading="marketLoading">
            <el-table
              :data="marketData"
              style="width: 100%">
              <el-table-column prop="symbol" label="指数代码" width="120"></el-table-column>
              <el-table-column prop="name" label="指数名称" width="150"></el-table-column>
              <el-table-column prop="last" label="最新价" width="100"></el-table-column>
              <el-table-column prop="change" label="涨跌" width="100">
                <template slot-scope="scope">
                  <span :class="scope.row.change >= 0 ? 'profit' : 'loss'">
                    {{ scope.row.change >= 0 ? '+' : '' }}{{ scope.row.change }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="changePercent" label="涨跌幅" width="100">
                <template slot-scope="scope">
                  <span :class="scope.row.changePercent >= 0 ? 'profit' : 'loss'">
                    {{ scope.row.changePercent >= 0 ? '+' : '' }}{{ scope.row.changePercent }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="open" label="开盘价" width="100"></el-table-column>
              <el-table-column prop="high" label="最高价" width="100"></el-table-column>
              <el-table-column prop="low" label="最低价" width="100"></el-table-column>
              <el-table-column prop="updateTime" label="更新时间"></el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      statusItems: [
        { title: '数据服务', status: true, icon: 'el-icon-s-data' },
        { title: '交易服务', status: true, icon: 'el-icon-s-finance' },
        { title: '策略引擎', status: true, icon: 'el-icon-s-operation' }
      ],
      marketLoading: false,
      marketData: [
        {
          symbol: '000001',
          name: '上证指数',
          last: 3450.68,
          change: 15.23,
          changePercent: 0.44,
          open: 3435.45,
          high: 3455.67,
          low: 3430.12,
          updateTime: '2024-04-13 15:00:00'
        },
        {
          symbol: '399001',
          name: '深证成指',
          last: 13567.89,
          change: -45.67,
          changePercent: -0.34,
          open: 13613.56,
          high: 13650.23,
          low: 13550.45,
          updateTime: '2024-04-13 15:00:00'
        },
        {
          symbol: '399006',
          name: '创业板指',
          last: 2678.45,
          change: 12.34,
          changePercent: 0.46,
          open: 2666.11,
          high: 2685.67,
          low: 2660.23,
          updateTime: '2024-04-13 15:00:00'
        },
        {
          symbol: '000300',
          name: '沪深300',
          last: 4567.89,
          change: 23.45,
          changePercent: 0.52,
          open: 4544.44,
          high: 4575.67,
          low: 4540.12,
          updateTime: '2024-04-13 15:00:00'
        }
      ]
    }
  },
  methods: {
    refreshMarketInfo() {
      this.marketLoading = true;
      setTimeout(() => {
        this.marketLoading = false;
        this.$message.success('市场数据已刷新');
      }, 1000);
    }
  },
  created() {
    this.refreshMarketInfo();
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}
.welcome-card {
  margin-bottom: 20px;
}
.welcome-header {
  text-align: center;
  padding: 20px 0;
}
.welcome-header h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #409EFF;
}
.welcome-header p {
  margin: 0;
  color: #606266;
}
.system-status {
  padding: 10px 0;
}
.system-status h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #303133;
}
.status-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 10px;
}
.status-icon {
  font-size: 24px;
  color: #409EFF;
  margin-right: 15px;
}
.status-info {
  flex: 1;
}
.status-title {
  font-size: 16px;
  margin-bottom: 5px;
  color: #303133;
}
.feature-card {
  height: 250px;
  display: flex;
  flex-direction: column;
}
.feature-card .el-card__body {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  padding: 0;
}
.feature-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  height: 100%;
}
.feature-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 15px;
}
.feature-description {
  text-align: center;
  margin-bottom: 15px;
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
