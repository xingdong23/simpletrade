<template>
  <div class="strategy-create-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>{{ isEditing ? '编辑策略' : '创建新策略' }}</span>
         <el-button style="float: right; padding: 3px 0" type="text" @click="goBack">返回列表</el-button>
      </div>
      
      <el-form :model="strategyForm" :rules="rules" ref="strategyForm" label-width="120px">
        <el-form-item label="策略名称" prop="name">
          <el-input v-model="strategyForm.name" placeholder="请输入策略名称"></el-input>
        </el-form-item>
        
        <el-form-item label="策略类型" prop="type">
            <el-select v-model="strategyForm.type" placeholder="选择策略类型">
                <el-option label="CTA策略" value="cta"></el-option>
                <el-option label="选股策略" value="stock"></el-option>
                <el-option label="套利策略" value="arbitrage"></el-option>
            </el-select>
        </el-form-item>
        
        <el-form-item label="策略模板/文件" prop="template">
           <!-- TODO: Implement selection or upload based on backend capabilities -->
           <el-select v-model="strategyForm.template" placeholder="选择策略模板">
               <el-option label="双均线 (DualMA)" value="DualMA"></el-option>
               <el-option label="布林带 (Bollinger)" value="Bollinger"></el-option>
               <el-option label="自定义..." value="custom"></el-option>
           </el-select>
           <!-- Or potentially an upload component if using custom files -->
        </el-form-item>
        
        <el-form-item label="交易品种" prop="symbols">
            <el-select
                v-model="strategyForm.symbols"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="请输入或选择交易品种">
                <!-- TODO: Load symbol options dynamically -->
                <el-option
                  v-for="item in symbolOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value">
                </el-option>
            </el-select>
        </el-form-item>
        
        <el-form-item label="K线周期" prop="interval">
            <el-select v-model="strategyForm.interval" placeholder="选择K线周期">
                <el-option label="1分钟" value="1m"></el-option>
                <el-option label="5分钟" value="5m"></el-option>
                <el-option label="15分钟" value="15m"></el-option>
                <el-option label="30分钟" value="30m"></el-option>
                <el-option label="1小时" value="1h"></el-option>
                <el-option label="日线" value="1d"></el-option>
            </el-select>
        </el-form-item>

        <el-divider>策略参数</el-divider>
        <!-- TODO: Dynamically generate parameter fields based on selected template -->
         <el-form-item v-for="(param, index) in strategyForm.parameters" :key="index" :label="param.label || `参数 ${index + 1}`">
            <el-input v-model="param.value" :placeholder="param.placeholder || '请输入参数值'"></el-input>
            <!-- Consider different input types based on param type (number, string, boolean) -->
        </el-form-item>
        <el-button type="text" @click="addParameter">添加参数</el-button> <!-- For custom params -->
        
        <el-divider>运行设置</el-divider>
         <el-form-item label="初始资金" prop="initialCapital">
              <el-input-number v-model="strategyForm.initialCapital" :min="0" :step="10000"></el-input-number>
         </el-form-item>
        <!-- Add other settings like commission, slippage if needed -->

        <el-form-item style="margin-top: 20px;">
          <el-button type="primary" @click="submitForm('strategyForm')" :loading="submitting">{{ isEditing ? '保存修改' : '创建策略' }}</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'StrategyCreate',
  data() {
    return {
      isEditing: false,
      strategyId: null,
      submitting: false,
      strategyForm: {
        name: '',
        type: 'cta',
        template: '',
        symbols: [],
        interval: '1d',
        parameters: [
            // Example dynamic parameter structure
            // { key: 'fast_period', label: '快线周期', value: '12', type: 'number' },
            // { key: 'slow_period', label: '慢线周期', value: '26', type: 'number' },
        ],
        initialCapital: 100000,
      },
      symbolOptions: [ // Placeholder
        { value: 'IF2106', label: 'IF2106' },
        { value: 'rb2110', label: 'rb2110' },
      ],
      rules: {
        name: [{ required: true, message: '请输入策略名称', trigger: 'blur' }],
        type: [{ required: true, message: '请选择策略类型', trigger: 'change' }],
        template: [{ required: true, message: '请选择策略模板', trigger: 'change' }],
        symbols: [{ required: true, message: '请至少选择一个交易品种', trigger: 'change' }],
        interval: [{ required: true, message: '请选择K线周期', trigger: 'change' }]
      }
    }
  },
  methods: {
    goBack() {
      this.$router.push('/strategy/index');
    },
    loadStrategyData(id) {
      this.submitting = true;
      // TODO: Call API to fetch strategy data for editing
      console.log('Loading strategy data for id:', id);
      setTimeout(() => {
           // Simulate loading existing data
           this.strategyForm = {
                name: '双均线策略 (编辑)',
                type: 'CTA',
                template: 'DualMA',
                symbols: ['IF2106', 'rb2110'],
                interval: '1h',
                parameters: [
                    { key: 'fast_ma', label: '快线周期', value: '10' },
                    { key: 'slow_ma', label: '慢线周期', value: '20' }
                ],
                initialCapital: 150000,
           };
           this.submitting = false;
           this.$message.success('策略数据已加载 (模拟)');
      }, 1000);
    },
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.submitting = true;
          // TODO: Call API to save (create or update) strategy
          const payload = { ...this.strategyForm };
          // Convert parameters array to object if needed by backend
          // payload.parameters = {}; 
          // this.strategyForm.parameters.forEach(p => { payload.parameters[p.key] = p.value; });
          
          console.log('Submitting strategy data:', payload);
          
          setTimeout(() => {
            this.submitting = false;
            this.$message({
              message: `${this.isEditing ? '更新' : '创建'}成功 (模拟)`,
              type: 'success'
            });
            this.goBack(); // Go back to list after successful submission
          }, 1500);

        } else {
          console.log('error submit!!');
          return false;
        }
      });
    },
    addParameter() {
        this.strategyForm.parameters.push({ key: '', label: '', value: '', placeholder: '自定义参数' });
    }
    // TODO: Method to load parameters based on selected template
  },
  created() {
    if (this.$route.query.id) {
      this.isEditing = true;
      this.strategyId = this.$route.query.id;
      this.loadStrategyData(this.strategyId);
    }
     // TODO: Fetch dynamic symbol options
  }
}
</script>

<style scoped>
.strategy-create-container {
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
.el-select {
    width: 100%;
}
</style> 