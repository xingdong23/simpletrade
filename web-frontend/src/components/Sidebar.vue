<template>
  <el-menu
    :default-active="activeIndex"
    class="sidebar-menu"
    :collapse="isCollapse"
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409EFF"
    router>
    
    <div class="logo-container">
      <!-- <img src="../assets/logo.png" alt="Logo" class="logo" v-if="!isCollapse"> -->
      <span class="title" v-if="!isCollapse">SimpleTrade</span>
    </div>
    
    <el-menu-item index="/">
      <i class="el-icon-s-home"></i>
      <span slot="title">仪表盘</span>
    </el-menu-item>
    
    <el-submenu index="data">
      <template slot="title">
        <i class="el-icon-s-data"></i>
        <span>数据管理</span>
      </template>
      <el-menu-item index="/data">数据概览</el-menu-item>
      <el-menu-item index="/data/import">数据导入</el-menu-item>
      <el-menu-item index="/data/export">数据导出</el-menu-item>
    </el-submenu>
    
    <el-submenu index="analysis">
      <template slot="title">
        <i class="el-icon-s-marketing"></i>
        <span>数据分析</span>
      </template>
      <el-menu-item index="/analysis">技术指标</el-menu-item>
      <el-menu-item index="/analysis/charts">图表分析</el-menu-item>
    </el-submenu>
    
    <el-submenu index="trading">
      <template slot="title">
        <i class="el-icon-s-finance"></i>
        <span>交易中心</span>
      </template>
      <el-menu-item index="/trading">交易下单</el-menu-item>
      <el-menu-item index="/trading/positions">持仓管理</el-menu-item>
      <el-menu-item index="/trading/orders">订单管理</el-menu-item>
    </el-submenu>
    
    <el-submenu index="strategy">
      <template slot="title">
        <i class="el-icon-s-operation"></i>
        <span>策略管理</span>
      </template>
      <el-menu-item index="/strategy">策略列表</el-menu-item>
      <el-menu-item index="/strategy/create">创建策略</el-menu-item>
    </el-submenu>
    
    <el-menu-item index="/backtest">
      <i class="el-icon-s-opportunity"></i>
      <span slot="title">回测系统</span>
    </el-menu-item>
    
    <el-menu-item index="/ai">
      <i class="el-icon-s-platform"></i>
      <span slot="title">AI分析</span>
    </el-menu-item>
    
    <el-menu-item index="/settings">
      <i class="el-icon-setting"></i>
      <span slot="title">系统设置</span>
    </el-menu-item>
  </el-menu>
</template>

<script>
export default {
  name: 'Sidebar',
  props: {
    isCollapse: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    activeIndex() {
      return this.$route.path;
    }
  }
}
</script>

<style scoped>
.sidebar-menu {
  height: 100%;
  border-right: none;
}
.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}
.logo-container {
  height: 60px;
  padding: 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}
.logo {
  width: 32px;
  height: 32px;
  margin-right: 10px;
}
.title {
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}
</style>
