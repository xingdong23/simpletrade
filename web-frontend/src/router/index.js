import { createRouter, createWebHistory } from 'vue-router'
// Remove import for missing HomeView
// import HomeView from '../views/HomeView.vue'
// 可能存在的旧数据管理视图导入，需要删除
// import DataManagement from '../views/DataManagement.vue'

const routes = [
  // Remove route for HomeView
  // {
  //   path: '/',
  //   name: 'home',
  //   component: HomeView
  // },
  // Remove route for AboutView
  // {
  //   path: '/about',
  //   name: 'about',
  //   // route level code-splitting
  //   // this generates a separate chunk (about.[hash].js) for this route
  //   // which is lazy-loaded when the route is visited.
  //   component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  // },
  // --- 开始移除旧路由 ---
  // {
  //   path: '/data-management',
  //   name: 'dataManagement',
  //   component: DataManagement // 假设存在此视图
  // },
  // --- 结束移除旧路由 ---

  // +++ 开始添加新模块的占位路由 +++
  {
    // Add a default route redirecting to strategy center, for example
    path: '/',
    redirect: '/strategy-center'
  },
  {
    path: '/strategy-center',
    name: 'strategyCenter',
    // 稍后创建对应的视图组件
    component: () => import(/* webpackChunkName: "strategy" */ '../views/StrategyCenterView.vue')
  },
  {
    path: '/trading-center',
    name: 'tradingCenter',
    component: () => import(/* webpackChunkName: "trading" */ '../views/TradingCenterView.vue')
  },
  {
    path: '/ai-analysis',
    name: 'aiAnalysis',
    component: () => import(/* webpackChunkName: "ai" */ '../views/AiAnalysisView.vue')
  },
  {
    path: '/user-center',
    name: 'userCenter',
    component: () => import(/* webpackChunkName: "user" */ '../views/UserCenterView.vue')
  }
  // +++ 结束添加新模块的占位路由 +++
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
