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
    path: '/strategy/:id',
    name: 'StrategyDetail',
    component: () => import(/* webpackChunkName: "strategy-detail" */ '../views/StrategyDetailView.vue'),
    props: true
  },
  {
    path: '/create-from-template/:templateId',
    name: 'CreateFromTemplate',
    component: () => import(/* webpackChunkName: "create-template" */ '../views/CreateFromTemplateView.vue'),
    props: true
  },
  {
    path: '/trading-center',
    name: 'tradingCenter',
    component: () => import(/* webpackChunkName: "trading" */ '../views/TradingCenterView.vue')
  },
  // 暂时注释掉AI分析路由，因为AIAnalysisView.vue文件可能不存在
  // {
  //   path: '/ai-analysis',
  //   name: 'aiAnalysis',
  //   component: () => import(/* webpackChunkName: "ai" */ '../views/AIAnalysisView.vue')
  // },
  {
    path: '/user-center',
    name: 'userCenter',
    component: () => import(/* webpackChunkName: "user" */ '../views/UserCenterView.vue')
  },
  {
    path: '/backtest',
    name: 'BacktestPage',
    component: () => import(/* webpackChunkName: "backtest" */ '../views/BacktestPageView.vue')
  },
  {
    path: '/backtest/:strategyId',
    name: 'BacktestPageWithStrategy',
    component: () => import(/* webpackChunkName: "backtest-strategy" */ '../views/BacktestPageView.vue'),
    props: true // Allows strategyId to be passed as a prop to the component
  },
  {
    path: '/backtests/report/:backtest_id',
    name: 'BacktestReport',
    component: () => import(/* webpackChunkName: "backtest-report" */ '../views/BacktestReportView.vue'),
    props: true // Allows backtest_id to be passed as a prop to the component
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
