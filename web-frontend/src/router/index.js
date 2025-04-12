import Vue from 'vue'
import VueRouter from 'vue-router'
import Layout from '../components/Layout.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Home.vue'),
        meta: { title: '仪表盘' }
      }
    ]
  },
  // { // Comment out or remove old /data route
  //   path: '/data',
  //   component: Layout,
  //   redirect: '/data/index',
  //   meta: { title: '数据管理' },
  //   children: [
  //     {
  //       path: 'index',
  //       name: 'DataOverview',
  //       component: () => import('../views/Data.vue'),
  //       meta: { title: '数据概览' }
  //     },
  //     {
  //       path: 'import',
  //       name: 'DataImport',
  //       component: () => import('../views/data/Import.vue'),
  //       meta: { title: '数据导入' }
  //     },
  //     {
  //       path: 'export',
  //       name: 'DataExport',
  //       component: () => import('../views/data/Export.vue'),
  //       meta: { title: '数据导出' }
  //     }
  //   ]
  // },
  {
    path: '/market-data', // Add new route for MarketData
    component: Layout,
    children: [
      {
        path: '',
        name: 'MarketData',
        component: () => import('../views/MarketData.vue'), // Point to the new component
        meta: { title: '行情数据' } // Update title
      }
    ]
  },
  // { // Comment out or remove old /analysis route
  //   path: '/analysis',
  //   component: Layout,
  //   redirect: '/analysis/index',
  //   meta: { title: '数据分析' },
  //   children: [
  //     {
  //       path: 'index',
  //       name: 'AnalysisIndex',
  //       component: () => import('../views/Analysis.vue'),
  //       meta: { title: '技术指标' }
  //     },
  //     {
  //       path: 'charts',
  //       name: 'AnalysisCharts',
  //       component: () => import('../views/analysis/Charts.vue'),
  //       meta: { title: '图表分析' }
  //     }
  //   ]
  // },
  {
    path: '/trading',
    component: Layout,
    redirect: '/trading/index',
    meta: { title: '交易中心' },
    children: [
      {
        path: 'index',
        name: 'TradingIndex',
        component: () => import('../views/trading/Index.vue'),
        meta: { title: '交易下单' }
      },
      {
        path: 'positions',
        name: 'TradingPositions',
        component: () => import('../views/trading/Positions.vue'),
        meta: { title: '持仓管理' }
      },
      {
        path: 'orders',
        name: 'TradingOrders',
        component: () => import('../views/trading/Orders.vue'),
        meta: { title: '订单管理' }
      }
    ]
  },
  {
    path: '/strategy',
    component: Layout,
    redirect: '/strategy/index',
    meta: { title: '策略管理' },
    children: [
      {
        path: 'index',
        name: 'StrategyIndex',
        component: () => import('../views/strategy/Index.vue'),
        meta: { title: '策略列表' }
      },
      {
        path: 'create',
        name: 'StrategyCreate',
        component: () => import('../views/strategy/Create.vue'),
        meta: { title: '创建策略' }
      }
    ]
  },
  {
    path: '/backtest',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Backtest',
        component: () => import('../views/Backtest.vue'),
        meta: { title: '回测系统' }
      }
    ]
  },
  {
    path: '/ai',
    component: Layout,
    children: [
      {
        path: '',
        name: 'AI',
        component: () => import('../views/AI.vue'),
        meta: { title: 'AI分析' }
      }
    ]
  },
  {
    path: '/settings',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Settings',
        component: () => import('../views/Settings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
