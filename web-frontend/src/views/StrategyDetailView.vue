<template>
  <div class="strategy-detail-container">
    <div class="page-header">
      <el-page-header 
        @back="goBack" 
        :content="strategy ? strategy.name : '策略详情'" 
        title="返回">
      </el-page-header>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content" v-loading="loading">
      <!-- 不再需要 Tabs, 直接显示信息 -->
      <div v-if="error" class="error-message">
         加载策略详情失败：{{ error }}
      </div>
      <div v-else-if="strategy">
          <!-- 策略基本信息 -->
          <el-descriptions :column="2" border title="基本信息">
            <el-descriptions-item label="策略名称">{{ strategy.name }}</el-descriptions-item>
            <el-descriptions-item label="标识符">{{ strategy.identifier }}</el-descriptions-item>
            <el-descriptions-item label="类型">{{ strategy.type }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ strategy.category || '-' }}</el-descriptions-item>
            <el-descriptions-item label="复杂度">
              <el-rate v-model="strategy.complexity" disabled></el-rate>
            </el-descriptions-item>
             <el-descriptions-item label="资源需求">
               <el-rate v-model="strategy.resource_requirement" disabled></el-rate>
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ strategy.description || '无' }}</el-descriptions-item>
          </el-descriptions>

          <!-- 策略默认参数 -->
          <div style="margin-top: 20px;">
            <h3>默认参数</h3>
            <el-table :data="parameterList" style="width: 100%" border size="small">
                <el-table-column prop="name" label="参数名" width="180"></el-table-column>
                <el-table-column prop="default" label="默认值"></el-table-column>
                <el-table-column prop="description" label="描述"></el-table-column>
                <!-- 可以根据需要添加 type, min, max 等列 -->
            </el-table>
          </div>

           <!-- 策略代码显示 -->
           <div v-if="strategy.code" style="margin-top: 20px;">
              <h3>策略代码示例</h3>
              <el-card shadow="never" style="max-height: 600px; overflow-y: auto;">
                  <pre style="margin: 0;"><code class="language-python">{{ strategy.code }}</code></pre>
              </el-card>
           </div>
           
           <!-- (可选) 添加"使用此模板创建我的策略"按钮 -->
           <div style="margin-top: 30px; text-align: center;">
               <el-button type="success" icon="el-icon-plus" @click="handleUseTemplate">使用此模板创建我的策略</el-button>
           </div>
      </div>
       <div v-else-if="!loading">
          未找到策略信息。
      </div>
      <!-- 原有的 Tabs 和其他 Pane 已移除 -->
    </div>
  </div>
</template>

<script>
// 只保留需要的 import
import { getStrategyDetail } from '@/api/strategies';
// import dayjs from 'dayjs'; // 不再需要

export default {
  name: 'StrategyDetailView',
  props: {
    id: { 
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      strategy: null,
      loading: false, 
      error: null,
      // --- 移除所有与回测、优化、实盘相关的 data --- 
      // activeTab: 'info',
      // strategyComplexity: 3,
      // strategyParams: {},
      // backtestLoading: false, 
      // backtestSymbol: '',
      // ... (移除其他 backtest 相关)
      // backtestResult: { hasResult: false, statistics: {} },
      // optimizeParams: { ... },
      // optimizeResult: { ... },
      // liveTradeRecords: []
    };
  },
  computed: {
    // parameterList 计算属性保持不变，用于展示默认参数
    parameterList() {
      if (!this.strategy || !this.strategy.parameters || typeof this.strategy.parameters !== 'object') {
        return [];
      }
      // 改造一下，确保即使后端没提供 details，也能显示默认值
      return Object.entries(this.strategy.parameters).map(([name, defaultValue]) => ({
        name,
        default: defaultValue,
        // 尝试从 strategy.class_details 获取描述 (如果后端返回了)
        description: this.strategy.class_details?.parameters?.[name]?.description || ''
      }));
    }
  },
  methods: {
    goBack() {
      this.$router.go(-1); // 改为返回上一页，通常更友好
    },
    // fetchStrategyDetail 保持不变
    async fetchStrategyDetail() {
      console.log('StrategyDetailView: fetchStrategyDetail() called with id:', this.id);
      this.loading = true;
      this.error = null;
      this.strategy = null; // 先清空
      try {
        const response = await getStrategyDetail(this.id);
        if (response.data && response.data.success) {
          this.strategy = response.data.data;
        } else {
          this.error = response.data.message || '获取策略详情失败';
        }
      } catch (err) {
        console.error('Error fetching strategy detail:', err);
        this.error = (err.response && err.response.data && err.response.data.message)
                       || (err.response && err.response.data && err.response.detail) 
                       || err.message 
                       || '网络错误或服务器内部错误';
      } finally {
        this.loading = false;
      }
    },
    // --- 移除所有与回测、优化、实盘相关的方法 --- 
    // runBacktest() { ... }
    // formatPercent() { ... }
    // formatNumber() { ... }
    // saveStrategyParams() { ... }
    // deployToLive() { ... }
    // runOptimization() { ... }
    // applyOptimizedParams() { ... }
    // applyParamSet() { ... }
    // stopStrategy() { ... }
    
    // (可选) 处理"使用模板"按钮点击
    handleUseTemplate() {
        if (!this.strategy) return;
        // TODO: 实现跳转到创建"我的策略"页面的逻辑
        // 可能需要将 strategy.id, strategy.name, strategy.parameters 等信息带过去
        this.$message.info(`功能待开发：使用模板 ${this.strategy.name} (ID: ${this.strategy.id}) 创建我的策略`);
        // 示例跳转 (假设有这样一个路由):
        // this.$router.push({ 
        //     name: 'CreateMyStrategy', 
        //     query: { templateId: this.strategy.id } 
        // });
    }
  },
  created() {
    this.fetchStrategyDetail();
  },
  watch: {
    // Watch id 保持不变, 但不再需要重置回测状态
    id(newId, oldId) {
      console.log(`StrategyDetailView: Watcher triggered. ID changed from ${oldId} to ${newId}`); 
      if (newId && newId !== oldId) {
        this.fetchStrategyDetail();
      }
    }
  }
};
</script>

<style scoped>
/* ... (原有样式) ... */
.error-message {
    color: #F56C6C;
    padding: 20px;
    text-align: center;
}
</style>
