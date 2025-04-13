import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    // Add a default route redirecting to strategy center
    path: '/',
    redirect: '/strategy-center'
  },
  {
    path: '/strategy-center',
    name: 'strategyCenter',
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
    component: () => import(/* webpackChunkName: "ai" */ '../views/AIAnalysisView.vue')
  },
  {
    path: '/user-center',
    name: 'userCenter',
    component: () => import(/* webpackChunkName: "user" */ '../views/UserCenterView.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
