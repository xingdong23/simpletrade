<template>
  <!-- No changes to template section -->
</template>

<script>
export default {
  computed: {
    pageTitle() {
      const routeMap = {
        '/strategy-center': '策略中心',
        '/trading-center': '交易中心',
        '/ai-analysis': 'AI分析',
        '/user-center': '用户中心'
      };
      // 如果当前路径不在 routeMap 中，就返回空字符串
      return routeMap[this.$route.path] || '';
    }
  },
};
</script>

<style>
  /* No changes to style section */
</style> 