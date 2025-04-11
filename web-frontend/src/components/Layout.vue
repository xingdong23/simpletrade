<template>
  <div class="app-wrapper">
    <!-- 侧边栏 -->
    <div class="sidebar-container" :class="{'is-collapse': isCollapse}">
      <div class="toggle-button" @click="toggleSidebar">
        <i :class="isCollapse ? 'el-icon-s-unfold' : 'el-icon-s-fold'"></i>
      </div>
      <Sidebar :is-collapse="isCollapse" />
    </div>
    
    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <div class="navbar">
        <div class="left">
          <breadcrumb />
        </div>
        <div class="right">
          <el-dropdown trigger="click">
            <span class="el-dropdown-link">
              <i class="el-icon-user"></i> 管理员 <i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item>个人信息</el-dropdown-item>
              <el-dropdown-item>修改密码</el-dropdown-item>
              <el-dropdown-item divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 内容区 -->
      <div class="app-main">
        <transition name="fade-transform" mode="out-in">
          <router-view />
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import Sidebar from './Sidebar.vue'
import Breadcrumb from './Breadcrumb.vue'

export default {
  name: 'Layout',
  components: {
    Sidebar,
    Breadcrumb
  },
  data() {
    return {
      isCollapse: false
    }
  },
  methods: {
    toggleSidebar() {
      this.isCollapse = !this.isCollapse
    }
  }
}
</script>

<style scoped>
.app-wrapper {
  position: relative;
  height: 100%;
  width: 100%;
  display: flex;
}

.sidebar-container {
  transition: width 0.28s;
  width: 220px;
  height: 100%;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1001;
  background-color: #304156;
}

.sidebar-container.is-collapse {
  width: 64px;
}

.main-container {
  min-height: 100%;
  transition: margin-left 0.28s;
  margin-left: 220px;
  position: relative;
  width: calc(100% - 220px);
  overflow: hidden;
}

.sidebar-container.is-collapse + .main-container {
  margin-left: 64px;
  width: calc(100% - 64px);
}

.navbar {
  height: 50px;
  overflow: hidden;
  position: relative;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.toggle-button {
  position: absolute;
  top: 10px;
  right: -12px;
  width: 24px;
  height: 24px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1002;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.app-main {
  padding: 20px;
  height: calc(100vh - 50px);
  overflow: auto;
  background-color: #f0f2f5;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter,
.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}
</style>
