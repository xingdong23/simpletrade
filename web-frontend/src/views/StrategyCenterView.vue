<template>
  <div class="strategy-center">
    <!-- 顶部标签导航 -->
    <div class="mb-6 border-b border-gray-200">
      <ul class="flex flex-wrap -mb-px text-sm font-medium text-center">
        <li class="mr-2">
          <a
            href="#"
            @click.prevent="activeTab = 'library'"
            :class="[activeTab === 'library' ? 'border-blue-600 text-blue-600' : 'border-transparent hover:border-gray-300 hover:text-gray-600', 'inline-block p-4 border-b-2 rounded-t-lg']"
          >
            策略库
          </a>
        </li>
        <li class="mr-2">
          <a
            href="#"
            @click.prevent="activeTab = 'builder'"
            :class="[activeTab === 'builder' ? 'border-blue-600 text-blue-600' : 'border-transparent hover:border-gray-300 hover:text-gray-600', 'inline-block p-4 border-b-2 rounded-t-lg']"
          >
            策略构建器
          </a>
        </li>
        <li class="mr-2">
          <a
            href="#"
            @click.prevent="activeTab = 'my-strategies'"
            :class="[activeTab === 'my-strategies' ? 'border-blue-600 text-blue-600' : 'border-transparent hover:border-gray-300 hover:text-gray-600', 'inline-block p-4 border-b-2 rounded-t-lg']"
          >
            我的策略
          </a>
        </li>
      </ul>
    </div>

    <!-- 策略库 -->
    <div v-if="activeTab === 'library'" class="strategy-library">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold text-gray-800">策略库</h2>
        <div class="flex space-x-2">
          <div class="relative">
            <input
              type="text"
              placeholder="搜索策略..."
              class="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
            <div class="absolute left-3 top-2.5 text-gray-400">
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          <select class="border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option value="all">所有类型</option>
            <option value="cta">CTA策略</option>
            <option value="ai">AI策略</option>
          </select>
        </div>
      </div>

      <!-- 策略卡片列表 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- 策略卡片 1 -->
        <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
          <div class="p-6">
            <div class="flex justify-between items-start">
              <h3 class="text-lg font-semibold text-gray-800">双均线突破策略</h3>
              <span class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">CTA策略</span>
            </div>
            <p class="mt-2 text-sm text-gray-600">基于双均线的突破交易策略，适用于趋势型市场。</p>
            <div class="mt-4 flex items-center text-sm text-gray-500">
              <span class="mr-4">胜率: <span class="font-medium text-green-600">58%</span></span>
              <span>年化收益: <span class="font-medium text-green-600">15.2%</span></span>
            </div>
            <div class="mt-6 flex justify-between">
              <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                查看详情
              </button>
              <button class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                使用策略
              </button>
            </div>
          </div>
        </div>

        <!-- 策略卡片 2 -->
        <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
          <div class="p-6">
            <div class="flex justify-between items-start">
              <h3 class="text-lg font-semibold text-gray-800">LSTM预测模型</h3>
              <span class="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full">AI策略</span>
            </div>
            <p class="mt-2 text-sm text-gray-600">基于深度学习LSTM网络的价格预测模型，适用于高频交易。</p>
            <div class="mt-4 flex items-center text-sm text-gray-500">
              <span class="mr-4">准确率: <span class="font-medium text-green-600">62%</span></span>
              <span>年化收益: <span class="font-medium text-green-600">18.7%</span></span>
            </div>
            <div class="mt-6 flex justify-between">
              <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                查看详情
              </button>
              <button class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                使用策略
              </button>
            </div>
          </div>
        </div>

        <!-- 策略卡片 3 -->
        <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
          <div class="p-6">
            <div class="flex justify-between items-start">
              <h3 class="text-lg font-semibold text-gray-800">海龟交易策略</h3>
              <span class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">CTA策略</span>
            </div>
            <p class="mt-2 text-sm text-gray-600">经典的海龟交易策略，基于突破信号进行趋势跟踪。</p>
            <div class="mt-4 flex items-center text-sm text-gray-500">
              <span class="mr-4">胜率: <span class="font-medium text-green-600">42%</span></span>
              <span>年化收益: <span class="font-medium text-green-600">22.1%</span></span>
            </div>
            <div class="mt-6 flex justify-between">
              <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                查看详情
              </button>
              <button class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                使用策略
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 策略构建器 -->
    <div v-if="activeTab === 'builder'" class="strategy-builder">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-6">策略构建器</h2>
        <p class="text-gray-600 mb-8">使用策略构建器创建自定义策略，无需编写代码。</p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <!-- 策略类型选择 -->
          <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-4">选择策略类型</h3>
            <div class="space-y-4">
              <div class="flex items-center">
                <input type="radio" id="cta-strategy" name="strategy-type" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                <label for="cta-strategy" class="ml-2 block text-sm font-medium text-gray-700">CTA策略</label>
              </div>
              <div class="flex items-center">
                <input type="radio" id="ai-strategy" name="strategy-type" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                <label for="ai-strategy" class="ml-2 block text-sm font-medium text-gray-700">AI策略</label>
              </div>
            </div>

            <h3 class="text-lg font-semibold text-gray-800 mt-8 mb-4">选择指标</h3>
            <div class="space-y-4">
              <div class="flex items-center">
                <input type="checkbox" id="ma" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                <label for="ma" class="ml-2 block text-sm font-medium text-gray-700">移动平均线 (MA)</label>
              </div>
              <div class="flex items-center">
                <input type="checkbox" id="rsi" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                <label for="rsi" class="ml-2 block text-sm font-medium text-gray-700">相对强弱指标 (RSI)</label>
              </div>
              <div class="flex items-center">
                <input type="checkbox" id="macd" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                <label for="macd" class="ml-2 block text-sm font-medium text-gray-700">MACD</label>
              </div>
              <div class="flex items-center">
                <input type="checkbox" id="bollinger" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                <label for="bollinger" class="ml-2 block text-sm font-medium text-gray-700">布林带 (Bollinger Bands)</label>
              </div>
            </div>
          </div>

          <!-- 策略参数设置 -->
          <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-4">策略参数</h3>
            <div class="space-y-4">
              <div>
                <label for="strategy-name" class="block text-sm font-medium text-gray-700 mb-1">策略名称</label>
                <input type="text" id="strategy-name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              </div>
              <div>
                <label for="ma-period" class="block text-sm font-medium text-gray-700 mb-1">MA周期</label>
                <input type="number" id="ma-period" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              </div>
              <div>
                <label for="rsi-period" class="block text-sm font-medium text-gray-700 mb-1">RSI周期</label>
                <input type="number" id="rsi-period" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              </div>
              <div>
                <label for="position-size" class="block text-sm font-medium text-gray-700 mb-1">仓位大小 (%)</label>
                <input type="number" id="position-size" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              </div>
            </div>

            <div class="mt-8">
              <button class="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                创建策略
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 我的策略 -->
    <div v-if="activeTab === 'my-strategies'" class="my-strategies">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold text-gray-800">我的策略</h2>
        <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
          新建策略
        </button>
      </div>

      <!-- 策略列表 -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">策略名称</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">类型</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">我的双均线策略</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">CTA策略</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">2023-10-15</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">运行中</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <a href="#" class="text-blue-600 hover:text-blue-900 mr-3">查看</a>
                <a href="#" class="text-red-600 hover:text-red-900">停止</a>
              </td>
            </tr>
            <tr>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">LSTM预测模型</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full">AI策略</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">2023-10-10</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">待运行</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <a href="#" class="text-blue-600 hover:text-blue-900 mr-3">查看</a>
                <a href="#" class="text-green-600 hover:text-green-900">启动</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StrategyCenterView',
  data() {
    return {
      activeTab: 'library' // 默认显示策略库标签页
    }
  }
}
</script>
