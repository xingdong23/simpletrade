<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Mobile menu button -->
    <button
      @click="toggleSidebar"
      class="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-gray-800 text-white focus:outline-none"
    >
      <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path v-if="sidebarOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>

    <!-- Backdrop -->
    <div
      v-if="sidebarOpen"
      @click="toggleSidebar"
      class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
    ></div>

    <!-- Sidebar -->
    <div
      :class="[sidebarOpen ? 'translate-x-0' : '-translate-x-full', 'lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-64 bg-gray-800 text-white transition-transform duration-300 ease-in-out']"
    >
      <div class="flex flex-col h-full">
        <!-- Logo/Brand -->
        <div class="h-16 flex items-center justify-center text-xl font-bold border-b border-gray-700">
          SimpleTrade
        </div>

        <!-- Navigation Links -->
        <nav class="flex-1 px-4 py-4 space-y-2 overflow-y-auto">
          <router-link to="/strategy-center" class="flex items-center px-4 py-2 rounded hover:bg-gray-700" :class="{'bg-blue-600': isActive('/strategy-center')}">
            <svg class="h-5 w-5 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            策略中心
          </router-link>

          <router-link to="/trading-center" class="flex items-center px-4 py-2 rounded hover:bg-gray-700" :class="{'bg-blue-600': isActive('/trading-center')}">
            <svg class="h-5 w-5 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            交易中心
          </router-link>

          <router-link to="/ai-analysis" class="flex items-center px-4 py-2 rounded hover:bg-gray-700" :class="{'bg-blue-600': isActive('/ai-analysis')}">
            <svg class="h-5 w-5 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            AI分析
          </router-link>

          <router-link to="/user-center" class="flex items-center px-4 py-2 rounded hover:bg-gray-700" :class="{'bg-blue-600': isActive('/user-center')}">
            <svg class="h-5 w-5 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            用户中心
          </router-link>
        </nav>

        <!-- API Status -->
        <div class="border-t border-gray-700 p-4">
          <div class="flex items-center justify-between">
            <span class="text-sm">API状态:</span>
            <span :class="apiStatus ? 'text-green-400' : 'text-red-400'" class="text-sm font-medium">
              {{ apiStatus ? '在线' : '离线' }}
            </span>
          </div>
          <button
            @click="checkApiStatus"
            class="mt-2 w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm focus:outline-none"
          >
            刷新状态
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden lg:ml-64">
      <header class="bg-white shadow z-10">
        <div class="px-4 py-4 flex justify-between items-center">
          <h2 class="text-xl font-semibold text-gray-800">{{ pageTitle }}</h2>
        </div>
      </header>
      <main class="flex-1 overflow-auto bg-gray-100 p-6">
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
      apiStatus: false,
      sidebarOpen: false
    }
  },
  computed: {
    pageTitle() {
      const routeMap = {
        '/strategy-center': '策略中心',
        '/trading-center': '交易中心',
        '/ai-analysis': 'AI分析中心',
        '/user-center': '用户中心'
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
    },
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    },
    isActive(path) {
      return this.$route.path.startsWith(path);
    }
  },
  mounted() {
    this.checkApiStatus();
  }
}
</script>
