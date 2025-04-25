<template>
  <div class="template-strategy-create">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>基于{{ templateName }}创建我的策略</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="goBack">返回</el-button>
      </div>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      
      <div v-else-if="error" class="error-message">
        加载策略模板失败：{{ error }}
      </div>
      
      <el-form v-else :model="strategyForm" :rules="rules" ref="strategyForm" label-width="120px">
        <el-form-item label="策略名称" prop="name">
          <el-input v-model="strategyForm.name" placeholder="请输入您的策略名称"></el-input>
        </el-form-item>
        
        <el-divider>策略参数</el-divider>
        
        <el-form-item v-for="(param, key) in originalParameters" :key="key" :label="param.description || key" :prop="'parameters.' + key">
          <el-input-number 
            v-if="param.type === 'int' || param.type === 'float'" 
            v-model="strategyForm.parameters[key]" 
            :precision="param.type === 'float' ? 2 : 0"
            :step="param.type === 'float' ? 0.1 : 1"
            :min="param.min !== undefined ? param.min : undefined"
            :max="param.max !== undefined ? param.max : undefined"
          ></el-input-number>
          <el-input v-else v-model="strategyForm.parameters[key]"></el-input>
          <div class="param-description" v-if="param.description">{{ param.description }}</div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting">创建我的策略</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { getStrategyDetail, createUserStrategy } from '@/api/strategies';

export default {
  name: 'CreateFromTemplateView',
  props: {
    templateId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      loading: true,
      submitting: false,
      error: null,
      templateName: '策略模板',
      originalParameters: {}, // 原始参数定义
      strategyForm: {
        name: '',
        parameters: {}
      },
      rules: {
        name: [
          { required: true, message: '请输入策略名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ]
      }
    };
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    
    async loadTemplateStrategy() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await getStrategyDetail(this.templateId);
        if (response.data && response.data.success) {
          const strategy = response.data.data;
          this.templateName = strategy.name;
          
          // 设置默认策略名称为"我的 + 模板名称"
          this.strategyForm.name = `我的${strategy.name}`;
          
          // 处理参数
          this.originalParameters = strategy.parameters || {};
          
          // 设置默认参数值
          const defaultParameters = {};
          Object.entries(this.originalParameters).forEach(([key, param]) => {
            defaultParameters[key] = param.default;
          });
          
          this.strategyForm.parameters = defaultParameters;
        } else {
          this.error = response.data.message || '获取策略模板失败';
        }
      } catch (err) {
        console.error('Error loading template strategy:', err);
        this.error = err.message || '网络错误或服务器内部错误';
      } finally {
        this.loading = false;
      }
    },
    
    async submitForm() {
      try {
        this.$refs.strategyForm.validate(async (valid) => {
          if (!valid) {
            return false;
          }
          
          this.submitting = true;
          
          // 构建请求数据
          const requestData = {
            user_id: 1, // 应该从用户会话或存储中获取
            strategy_id: parseInt(this.templateId),
            name: this.strategyForm.name,
            parameters: this.strategyForm.parameters
          };
          
          try {
            const response = await createUserStrategy(requestData);
            
            if (response.data && response.data.success) {
              this.$message.success('用户策略创建成功');
              // 跳转到策略中心页面
              this.$router.push('/strategy-center');
            } else {
              this.$message.error(response.data.message || '创建用户策略失败');
            }
          } catch (err) {
            console.error('Error creating user strategy:', err);
            this.$message.error(err.message || '网络错误或服务器内部错误');
          } finally {
            this.submitting = false;
          }
        });
      } catch (err) {
        console.error('Form validation error:', err);
        this.$message.error('表单验证失败');
        this.submitting = false;
      }
    }
  },
  created() {
    this.loadTemplateStrategy();
  }
};
</script>

<style scoped>
.template-strategy-create {
  padding: 20px;
}
.loading-container {
  padding: 20px;
}
.error-message {
  color: #F56C6C;
  padding: 20px;
  text-align: center;
}
.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both;
}
.param-description {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style> 