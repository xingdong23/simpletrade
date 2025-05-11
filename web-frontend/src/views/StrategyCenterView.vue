<template>
  <div>
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="策略列表" name="strategy-list">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">策略列表</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-input
                v-model="searchQuery"
                placeholder="搜索策略..."
                prefix-icon="el-icon-search"
                style="width: 200px; margin-right: 10px;"
                @input="filterStrategies"
              ></el-input>
              <el-select
                placeholder="策略类型"
                style="width: 150px;"
                v-model="selectedType" 
                @change="filterStrategies" 
                clearable
              >
                <el-option label="所有类型" value="all"></el-option>
                <el-option
                  v-for="type in strategyTypes" 
                  :key="type"
                  :label="getTypeLabel(type)"
                  :value="type"
                ></el-option>
              </el-select>
            </el-col>
          </el-row>
        </div>

        <el-row :gutter="20" type="flex" style="flex-wrap: wrap;">
          <el-col v-for="strategy in filteredStrategies" :key="strategy.id" :xs="24" :sm="12" :md="8" :lg="8" :xl="8" style="margin-bottom: 20px;">
            <el-card shadow="hover" class="strategy-card">
              <div class="strategy-card-content">
                <div class="strategy-card-header">
                  <h3 class="strategy-title">{{ strategy.name }}</h3>
                  <el-tag size="small" type="primary" v-if="strategy.category">{{ strategy.category }}</el-tag>
                  <el-tag size="small" type="info" v-else-if="strategy.type">{{ getTypeLabel(strategy.type) }}</el-tag>
                </div>
                <p class="strategy-description">{{ strategy.description || '暂无描述' }}</p>
                <div class="strategy-actions">
                  <el-button type="primary" size="small" @click="navigateToDetail(strategy.id)">查看详情</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="我的策略" name="my-strategies">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">我的策略</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="primary" icon="el-icon-plus">新建策略</el-button>
            </el-col>
          </el-row>
        </div>

        <el-table :data="myStrategiesList" style="width: 100%" border>
          <el-table-column prop="name" label="策略名称" width="180"></el-table-column>
          <el-table-column prop="type" label="类型" width="120">
            <template slot-scope="scope">
              <el-tag size="small">{{ getTypeLabel(scope.row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createTime" label="创建时间" width="180"></el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template slot-scope="scope">
              <el-tag 
                :type="scope.row.status === '运行中' ? 'success' : scope.row.status === '已初始化' ? 'warning' : scope.row.status === '未加载' ? 'info' : 'danger'" 
                size="small"
              >
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template slot-scope="scope">
              <el-button size="mini" type="text" @click="handleView(scope.row)">查看</el-button>
              <el-button size="mini" type="text" @click="handleBacktest(scope.row)">回测</el-button>
              <el-button size="mini" type="text" @click="handleOptimize(scope.row)">优化</el-button>
              <el-button
                size="mini"
                type="text"
                :type="scope.row.status === '运行中' ? 'danger' : 'success'"
                @click="handleAction(scope.row)"
              >
                {{ scope.row.status === '运行中' ? '停止' : '启动' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { getStrategies, getStrategyTypes, getUserStrategies } from '@/api/strategies'

export default {
  name: 'StrategyCenterView',
  data() {
    return {
      activeTab: 'strategy-list',
      allStrategies: [],
      filteredStrategies: [],
      strategyTypes: [],
      searchQuery: '',
      selectedType: 'all',
      myStrategiesList: [],
      currentUserId: 1
    }
  },
  created() {
    this.fetchAllStrategies()
    this.fetchStrategyTypes()
    this.fetchMyStrategies()
  },
  methods: {
    getTypeLabel(type) {
      const typeLabels = {
        'cta': 'CTA策略',
        'stock': '选股策略',
        'arbitrage': '套利策略',
        'grid': '网格策略',
        'trend': '趋势策略',
        'mean_reversion': '均值回归',
        'ai': 'AI策略'
      }
      return typeLabels[type] || type
    },
    
    filterStrategies() {
      this.filteredStrategies = this.allStrategies.filter(strategy => {
        const matchesSearch = !this.searchQuery || 
          strategy.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          (strategy.description && strategy.description.toLowerCase().includes(this.searchQuery.toLowerCase()))
        
        const matchesType = this.selectedType === 'all' || 
          strategy.type === this.selectedType
        
        return matchesSearch && matchesType
      })
    },
    
    fetchAllStrategies() {
      getStrategies()
        .then(response => {
          if (response.data && response.data.success) {
            this.allStrategies = response.data.data || []
            this.filteredStrategies = [...this.allStrategies]
          }
        })
    },
    
    fetchStrategyTypes() {
      getStrategyTypes()
        .then(response => {
          if (response.data && response.data.success) {
            this.strategyTypes = Array.isArray(response.data.data) ? response.data.data : []
          }
        })
    },
    
    fetchMyStrategies() {
      getUserStrategies(this.currentUserId)
        .then(response => {
          if (response.data && response.data.success) {
            this.myStrategiesList = response.data.data || []
          }
        })
    },
    
    navigateToDetail(strategyId) {
      this.$router.push('/strategy/' + strategyId)
    },
    
    handleView(row) {
      this.$router.push('/strategy/' + row.id)
    },
    
    handleBacktest(row) {
      this.$router.push({ name: 'BacktestPageWithStrategy', params: { strategyId: row.id } })
    },
    
    handleOptimize(row) {
      // 暂未实现
    },
    
    handleAction(row) {
      if (row.status === '运行中') {
        this.$confirm('确定要停止该策略吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          row.status = '待运行' // TODO: Call stop API
          this.$message({
            type: 'success',
            message: `策略 ${row.name} 已停止`
          })
          this.fetchMyStrategies()
        }).catch(() => {})
      } else {
        this.$message({
          type: 'info',
          message: `正在启动策略 ${row.name}...`
        })
        setTimeout(() => {
          row.status = '运行中' // TODO: Call start API
          this.$message.success(`策略 ${row.name} 已启动`)
          this.fetchMyStrategies()
        }, 1000)
      }
    }
  }
}
</script>

<style>
.strategy-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.strategy-card-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.strategy-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.strategy-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.strategy-description {
  flex-grow: 1;
  margin-bottom: 15px;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.strategy-actions {
  margin-top: auto;
}
</style>
