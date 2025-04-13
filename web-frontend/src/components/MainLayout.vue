<template>
  <el-container style="height: 100vh;">
    <!-- Sidebar -->
    <el-aside width="250px" style="background-color: #304156; color: white;">
      <div style="height: 60px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; border-bottom: 1px solid #1f2d3d;">
        SimpleTrade
      </div>

      <!-- Navigation Menu -->
      <el-menu
        :default-active="activeIndex"
        class="el-menu-vertical"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF">

        <el-menu-item index="/strategy-center" @click="$router.push('/strategy-center')">
          <i class="el-icon-s-data"></i>
          <span slot="title">策略中心</span>
        </el-menu-item>

        <el-menu-item index="/trading-center" @click="$router.push('/trading-center')">
          <i class="el-icon-s-finance"></i>
          <span slot="title">交易中心</span>
        </el-menu-item>

        <el-menu-item index="/ai-analysis" @click="$router.push('/ai-analysis')">
          <i class="el-icon-s-marketing"></i>
          <span slot="title">AI分析</span>
        </el-menu-item>

        <el-menu-item index="/user-center" @click="$router.push('/user-center')">
          <i class="el-icon-user"></i>
          <span slot="title">用户中心</span>
        </el-menu-item>
      </el-menu>


    </el-aside>

    <!-- Main Content -->
    <el-container>
      <el-header style="background-color: white; box-shadow: 0 1px 4px rgba(0,21,41,.08); line-height: 60px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2 style="font-size: 18px; font-weight: 600; color: #303133;">{{ pageTitle }}</h2>
          <div>
            <el-dropdown>
              <span class="el-dropdown-link">
                <el-avatar size="small" icon="el-icon-user"></el-avatar>
                <span style="margin-left: 8px;">张三</span>
                <i class="el-icon-arrow-down el-icon--right"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item icon="el-icon-user">个人中心</el-dropdown-item>
                <el-dropdown-item icon="el-icon-setting">账户设置</el-dropdown-item>
                <el-dropdown-item divided icon="el-icon-switch-button">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-main style="background-color: #f0f2f5; padding: 20px;">
        <slot></slot>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
export default {
  name: 'MainLayout',
  data() {
    return {
      sidebarOpen: false,
      activeIndex: ''
    }
  },
  computed: {
    pageTitle() {
      const routeMap = {
        '/strategy-center': '策略中心',
        '/trading-center': '交易中心',
        '/ai-analysis': 'AI分析',
        '/user-center': '用户中心'
      };
      return routeMap[this.$route.path] || '页面';
    }
  },
  methods: {

    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    },
    isActive(path) {
      return this.$route.path.startsWith(path);
    }
  },
  watch: {
    $route: {
      immediate: true,
      handler(route) {
        this.activeIndex = route.path;
      }
    }
  },
  mounted() {
    // 初始化组件
  }
}
</script>

<style>
.el-menu {
  border-right: none;
}

.el-menu-vertical:not(.el-menu--collapse) {
  width: 250px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}
</style>
