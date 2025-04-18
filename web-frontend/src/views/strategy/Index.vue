<template>
  <div class="strategy-index-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>策略列表</span>
        <el-button style="float: right;" type="primary" icon="el-icon-plus" @click="goToCreate">创建新策略</el-button>
      </div>
      
      <el-table
        :data="strategyList"
        style="width: 100%"
        border
        v-loading="loading">
        <el-table-column prop="name" label="策略名称" width="180"></el-table-column>
        <el-table-column prop="type" label="策略类型" width="120"></el-table-column>
        <el-table-column prop="symbols" label="交易品种" width="200">
           <template slot-scope="scope">
              {{ scope.row.symbols.join(', ') }}
           </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 'running' ? 'success' : 'info'">
              {{ scope.row.status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastUpdateTime" label="最后更新时间" width="180"></el-table-column>
        <el-table-column label="操作" fixed="right" width="250">
          <template slot-scope="scope">
            <el-button
              size="mini"
              :type="scope.row.status === 'running' ? 'warning' : 'success'"
              @click="toggleStrategy(scope.row)">
              {{ scope.row.status === 'running' ? '停止' : '启动' }}
            </el-button>
            <el-button
              size="mini"
              @click="editStrategy(scope.row)">编辑</el-button>
            <el-button
              size="mini"
              type="danger"
              @click="deleteStrategy(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

       <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total">
        </el-pagination>
      </div>

    </el-card>
  </div>
</template>

<script>
// 导入 API 函数
import { getStrategies } from '@/api/strategies' // 假设 @ 指向 src 目录

export default {
  name: 'StrategyIndex',
  data() {
    return {
      loading: false,
      strategyList: [
        // Placeholder data
        {
          id: 'strategy1',
          name: '双均线策略',
          type: 'CTA',
          symbols: ['IF2106', 'rb2110'],
          status: 'running',
          lastUpdateTime: '2024-04-13 14:30:00'
        },
        {
          id: 'strategy2',
          name: 'RSI选股',
          type: 'Stock',
          symbols: ['600000', '000001'],
          status: 'stopped',
          lastUpdateTime: '2024-04-12 10:00:00'
        }
      ],
      currentPage: 1,
      pageSize: 10,
      total: 2
    }
  },
  methods: {
    goToCreate() {
      this.$router.push('/strategy/create');
    },
    fetchStrategies() {
      this.loading = true;
      // console.log(`Fetching strategies page ${this.currentPage} size ${this.pageSize}`);
      // setTimeout(() => {
      //   // Update strategyList and total based on API response
      //   this.loading = false;
      //    this.$message.info('策略列表已刷新 (模拟)');
      // }, 1000);

      // 调用 API 获取数据
      // 注意：当前后端 API 和 api/strategies.js 中的 getStrategies 暂未支持分页参数
      // 如果需要分页，需要前后端同步修改
      getStrategies() // 暂不传递分页或过滤参数
        .then(response => {
          // 检查后端返回的数据结构
          if (response.data && response.data.success) {
            // 假设后端返回的数据在 response.data.data 中
            this.strategyList = response.data.data;
            // 注意：后端目前似乎没有返回 total，暂时用列表长度代替，如果需要准确分页，后端需返回 total
            this.total = this.strategyList.length; 
            this.$message.success('策略列表已更新');
          } else {
            // 处理后端返回的业务错误消息
            this.$message.error(response.data.message || '获取策略列表失败');
            this.strategyList = []; // 清空列表
            this.total = 0;
          }
        })
        .catch(error => {
          // 处理网络错误或其他JS异常
          console.error('获取策略列表失败:', error);
          this.$message.error('网络错误，无法获取策略列表');
          this.strategyList = []; // 清空列表
          this.total = 0;
        })
        .finally(() => {
          // 无论成功失败，最终都停止加载状态
          this.loading = false;
        });
    },
    toggleStrategy(row) {
      const action = row.status === 'running' ? '停止' : '启动';
      this.$confirm(`确定要${action}策略 ${row.name} 吗?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // TODO: Call API to start/stop strategy
        console.log(`${action} strategy:`, row);
        row.status = row.status === 'running' ? 'stopped' : 'running'; // Toggle status locally for demo
        this.$message({
          type: 'success',
          message: `${action}请求已发送!`
        });
      }).catch(() => {
        this.$message({ type: 'info', message: '已取消操作' });
      });
    },
    editStrategy(row) {
      // Navigate to create/edit page with strategy ID
      this.$router.push({ path: '/strategy/create', query: { id: row.id } });
    },
    deleteStrategy(row) {
       this.$confirm(`确定要删除策略 ${row.name} 吗? 此操作不可恢复。`, '警告', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error' // Use error type for deletion confirmation
      }).then(() => {
        // TODO: Call API to delete strategy
        console.log('Delete strategy:', row);
        this.strategyList = this.strategyList.filter(s => s.id !== row.id); // Remove locally for demo
        this.total = this.strategyList.length; // Update total for demo
        this.$message({ type: 'success', message: '删除请求已发送!' });
      }).catch(() => {
        this.$message({ type: 'info', message: '已取消删除' });
      });
    },
    handleSizeChange(val) {
      this.pageSize = val;
      this.fetchStrategies();
    },
    handleCurrentChange(val) {
      this.currentPage = val;
      this.fetchStrategies();
    }
  },
  created() {
    this.fetchStrategies();
  }
}
</script>

<style scoped>
.strategy-index-container {
  padding: 20px;
}
.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both
}
.pagination-container {
    margin-top: 20px;
    text-align: right;
}
</style> 