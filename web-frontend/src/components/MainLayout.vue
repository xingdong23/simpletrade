<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <div class="w-64 bg-white shadow-md">
      <div class="p-4 bg-blue-600">
        <h1 class="text-white text-xl font-bold">SimpleTrade</h1>
      </div>
      <nav class="mt-4">
        <ul>
          <li>
            <router-link to="/" class="block px-4 py-2 text-gray-700 hover:bg-blue-100 hover:text-blue-600">
              <i class="fas fa-home mr-2"></i> 仪表盘
            </router-link>
          </li>
          <li>
            <router-link to="/data" class="block px-4 py-2 text-gray-700 hover:bg-blue-100 hover:text-blue-600">
              <i class="fas fa-database mr-2"></i> 数据管理
            </router-link>
          </li>
          <li>
            <router-link to="/analysis" class="block px-4 py-2 text-gray-700 hover:bg-blue-100 hover:text-blue-600">
              <i class="fas fa-chart-line mr-2"></i> 数据分析
            </router-link>
          </li>
          <li>
            <router-link to="/trading" class="block px-4 py-2 text-gray-700 hover:bg-blue-100 hover:text-blue-600">
              <i class="fas fa-exchange-alt mr-2"></i> 交易中心
            </router-link>
          </li>
          <li>
            <router-link to="/strategy" class="block px-4 py-2 text-gray-700 hover:bg-blue-100 hover:text-blue-600">
              <i class="fas fa-cogs mr-2"></i> 策略管理
            </router-link>
          </li>
          <li>
            <router-link to="/backtest" class="block px-4 py-2 text-gray-700 hover:bg-blue-100 hover:text-blue-600">
              <i class="fas fa-history mr-2"></i> 回测系统
            </router-link>
          </li>
          <li>
            <router-link to="/ai" class="block px-4 py-2 text-gray-700 hover:bg-blue-100 hover:text-blue-600">
              <i class="fas fa-brain mr-2"></i> AI分析
            </router-link>
          </li>
        </ul>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-auto">
      <header class="bg-white shadow-sm">
        <div class="px-4 py-3 flex justify-between items-center">
          <h2 class="text-lg font-semibold text-gray-800">{{ pageTitle }}</h2>
          <div class="flex items-center">
            <span class="text-sm text-gray-600 mr-4">API状态: 
              <span :class="apiStatus ? 'text-green-600' : 'text-red-600'">
                {{ apiStatus ? '在线' : '离线' }}
              </span>
            </span>
            <button @click="checkApiStatus" class="px-3 py-1 bg-blue-100 text-blue-600 rounded-md text-sm hover:bg-blue-200">
              刷新
            </button>
          </div>
        </div>
      </header>
      <main class="p-6">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MainLayout',
  data() {
    return {
      apiStatus: false
    }
  },
  computed: {
    pageTitle() {
      const routeMap = {
        '/': '仪表盘',
        '/data': '数据管理',
        '/analysis': '数据分析',
        '/trading': '交易中心',
        '/strategy': '策略管理',
        '/backtest': '回测系统',
        '/ai': 'AI分析'
      };
      return routeMap[this.$route.path] || '页面';
    }
  },
  methods: {
    async checkApiStatus() {
      try {
        const response = await fetch('http://localhost:8000/docs');
        this.apiStatus = response.ok;
      } catch (error) {
        this.apiStatus = false;
        console.error('API连接错误:', error);
      }
    }
  },
  mounted() {
    this.checkApiStatus();
  }
}
</script>
