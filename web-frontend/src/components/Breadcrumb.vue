<template>
  <el-breadcrumb class="app-breadcrumb" separator="/">
    <transition-group name="breadcrumb">
      <el-breadcrumb-item v-for="(item, index) in levelList" :key="item.path">
        <span v-if="index === levelList.length - 1" class="no-redirect">{{ item.meta.title }}</span>
        <a v-else @click.prevent="handleLink(item)">{{ item.meta.title }}</a>
      </el-breadcrumb-item>
    </transition-group>
  </el-breadcrumb>
</template>

<script>
export default {
  name: 'Breadcrumb',
  data() {
    return {
      levelList: null
    }
  },
  watch: {
    $route() {
      this.getBreadcrumb()
    }
  },
  created() {
    this.getBreadcrumb()
  },
  methods: {
    getBreadcrumb() {
      // 面包屑仅显示有meta.title的路由
      let matched = this.$route.matched.filter(item => item.meta && item.meta.title)
      
      // 如果首页不在路由中，手动添加
      const first = matched[0]
      if (first && first.path !== '/') {
        matched = [{ path: '/', meta: { title: '首页' } }].concat(matched)
      }
      
      this.levelList = matched
    },
    handleLink(item) {
      const { path } = item
      this.$router.push(path)
    }
  }
}
</script>

<style scoped>
.app-breadcrumb {
  display: inline-block;
  font-size: 14px;
  line-height: 50px;
  margin-left: 8px;
}
.app-breadcrumb .no-redirect {
  color: #97a8be;
  cursor: text;
}
.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition: all 0.5s;
}
.breadcrumb-enter,
.breadcrumb-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
