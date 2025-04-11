<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <div slot="header">
            <h2>欢迎使用 SimpleTrade</h2>
          </div>
          <p>SimpleTrade 是一个简单易用的量化交易平台，提供数据管理、数据分析和策略回测等功能。</p>
          <p>使用左上角的导航菜单开始探索平台功能。</p>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card class="feature-card">
          <div slot="header">
            <h3>数据管理</h3>
          </div>
          <p>管理您的交易数据，包括导入、导出和查询功能。</p>
          <el-button type="primary" @click="$router.push('/data')">开始使用</el-button>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card">
          <div slot="header">
            <h3>数据分析</h3>
          </div>
          <p>使用技术指标分析您的交易数据，发现市场趋势。</p>
          <el-button type="primary" @click="$router.push('/analysis')">开始分析</el-button>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card">
          <div slot="header">
            <h3>策略回测</h3>
          </div>
          <p>回测您的交易策略，评估其在历史数据上的表现。</p>
          <el-button type="primary" @click="$router.push('/analysis')">开始回测</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
.welcome-card {
  margin-bottom: 20px;
}

.feature-card {
  height: 200px;
  display: flex;
  flex-direction: column;
}

.feature-card .el-card__body {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex-grow: 1;
}

.el-button {
  margin-top: auto;
}
</style>
