<template>
  <div class="trading-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>交易下单</span>
            <el-tag type="success" style="margin-left: 10px;" v-if="connected">已连接</el-tag>
            <el-tag type="danger" style="margin-left: 10px;" v-else>未连接</el-tag>
            <el-button style="float: right; padding: 3px 0" type="text" @click="connectGateway">
              {{ connected ? '断开连接' : '连接交易接口' }}
            </el-button>
          </div>
          
          <el-form :model="orderForm" label-width="100px" :rules="rules" ref="orderForm">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="交易接口" prop="gateway">
                  <el-select v-model="orderForm.gateway" placeholder="请选择交易接口">
                    <el-option label="老虎证券" value="tiger"></el-option>
                    <el-option label="盈透证券" value="ib"></el-option>
                    <el-option label="CTP" value="ctp"></el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="交易账户" prop="account">
                  <el-select v-model="orderForm.account" placeholder="请选择交易账户">
                    <el-option label="模拟账户" value="demo"></el-option>
                    <el-option label="实盘账户" value="real"></el-option>
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="交易所" prop="exchange">
                  <el-select v-model="orderForm.exchange" placeholder="请选择交易所" @change="handleExchangeChange">
                    <el-option label="上海证券交易所" value="SSE"></el-option>
                    <el-option label="深圳证券交易所" value="SZSE"></el-option>
                    <el-option label="中国金融期货交易所" value="CFFEX"></el-option>
                    <el-option label="上海期货交易所" value="SHFE"></el-option>
                    <el-option label="大连商品交易所" value="DCE"></el-option>
                    <el-option label="郑州商品交易所" value="CZCE"></el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="合约代码" prop="symbol">
                  <el-select v-model="orderForm.symbol" placeholder="请选择合约代码" filterable>
                    <el-option
                      v-for="item in symbolOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value">
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="方向" prop="direction">
                  <el-radio-group v-model="orderForm.direction">
                    <el-radio label="LONG">买入</el-radio>
                    <el-radio label="SHORT">卖出</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="开平" prop="offset">
                  <el-radio-group v-model="orderForm.offset">
                    <el-radio label="OPEN">开仓</el-radio>
                    <el-radio label="CLOSE">平仓</el-radio>
                    <el-radio label="CLOSETODAY">平今</el-radio>
                    <el-radio label="CLOSEYESTERDAY">平昨</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="价格类型" prop="orderType">
                  <el-select v-model="orderForm.orderType" placeholder="请选择价格类型">
                    <el-option label="限价单" value="LIMIT"></el-option>
                    <el-option label="市价单" value="MARKET"></el-option>
                    <el-option label="FAK单" value="FAK"></el-option>
                    <el-option label="FOK单" value="FOK"></el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="价格" prop="price" :required="orderForm.orderType === 'LIMIT'">
                  <el-input-number 
                    v-model="orderForm.price" 
                    :precision="2" 
                    :step="0.01" 
                    :min="0"
                    :disabled="orderForm.orderType === 'MARKET'"
                    controls-position="right">
                  </el-input-number>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="数量" prop="volume">
                  <el-input-number 
                    v-model="orderForm.volume" 
                    :precision="0" 
                    :step="1" 
                    :min="1"
                    controls-position="right">
                  </el-input-number>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <el-button type="primary" @click="submitOrder('orderForm')">下单</el-button>
                  <el-button @click="resetForm('orderForm')">重置</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>行情信息</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="refreshQuote">刷新</el-button>
          </div>
          <div v-if="currentQuote.symbol" class="quote-info">
            <div class="quote-header">
              <h3>{{ currentQuote.name }} ({{ currentQuote.symbol }})</h3>
              <div :class="['price', currentQuote.change >= 0 ? 'price-up' : 'price-down']">
                {{ currentQuote.last }}
                <span class="change">
                  {{ currentQuote.change >= 0 ? '+' : '' }}{{ currentQuote.change }} ({{ currentQuote.changePercent }}%)
                </span>
              </div>
            </div>
            <el-divider></el-divider>
            <div class="quote-details">
              <div class="quote-item">
                <span class="label">开盘价:</span>
                <span class="value">{{ currentQuote.open }}</span>
              </div>
              <div class="quote-item">
                <span class="label">最高价:</span>
                <span class="value">{{ currentQuote.high }}</span>
              </div>
              <div class="quote-item">
                <span class="label">最低价:</span>
                <span class="value">{{ currentQuote.low }}</span>
              </div>
              <div class="quote-item">
                <span class="label">昨收价:</span>
                <span class="value">{{ currentQuote.preClose }}</span>
              </div>
              <div class="quote-item">
                <span class="label">成交量:</span>
                <span class="value">{{ currentQuote.volume }}</span>
              </div>
              <div class="quote-item">
                <span class="label">成交额:</span>
                <span class="value">{{ currentQuote.turnover }}</span>
              </div>
              <div class="quote-item">
                <span class="label">更新时间:</span>
                <span class="value">{{ currentQuote.updateTime }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-quote">
            <p>请选择合约查看行情</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'TradingIndex',
  data() {
    return {
      connected: false,
      orderForm: {
        gateway: '',
        account: '',
        exchange: '',
        symbol: '',
        direction: 'LONG',
        offset: 'OPEN',
        orderType: 'LIMIT',
        price: 0,
        volume: 1
      },
      rules: {
        gateway: [{ required: true, message: '请选择交易接口', trigger: 'change' }],
        account: [{ required: true, message: '请选择交易账户', trigger: 'change' }],
        exchange: [{ required: true, message: '请选择交易所', trigger: 'change' }],
        symbol: [{ required: true, message: '请选择合约代码', trigger: 'change' }],
        direction: [{ required: true, message: '请选择方向', trigger: 'change' }],
        offset: [{ required: true, message: '请选择开平', trigger: 'change' }],
        orderType: [{ required: true, message: '请选择价格类型', trigger: 'change' }],
        volume: [{ required: true, message: '请输入数量', trigger: 'blur' }]
      },
      symbolOptions: [],
      currentQuote: {
        symbol: '',
        name: '',
        last: 0,
        change: 0,
        changePercent: 0,
        open: 0,
        high: 0,
        low: 0,
        preClose: 0,
        volume: 0,
        turnover: 0,
        updateTime: ''
      }
    }
  },
  methods: {
    connectGateway() {
      this.connected = !this.connected;
      this.$message({
        message: this.connected ? '交易接口连接成功' : '交易接口已断开',
        type: this.connected ? 'success' : 'warning'
      });
    },
    handleExchangeChange() {
      // 根据交易所获取合约列表
      this.symbolOptions = [
        { value: '600000', label: '浦发银行 (600000)' },
        { value: '601398', label: '工商银行 (601398)' },
        { value: '000001', label: '平安银行 (000001)' },
        { value: '000858', label: '五粮液 (000858)' }
      ];
      
      // 清空当前选择的合约
      this.orderForm.symbol = '';
      this.currentQuote = {
        symbol: '',
        name: '',
        last: 0,
        change: 0,
        changePercent: 0,
        open: 0,
        high: 0,
        low: 0,
        preClose: 0,
        volume: 0,
        turnover: 0,
        updateTime: ''
      };
    },
    submitOrder(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          if (!this.connected) {
            this.$message.error('请先连接交易接口');
            return;
          }
          
          // 调用API提交订单
          this.$message({
            message: '订单已提交',
            type: 'success'
          });
        } else {
          this.$message.error('请完善订单信息');
          return false;
        }
      });
    },
    resetForm(formName) {
      this.$refs[formName].resetFields();
    },
    refreshQuote() {
      if (!this.orderForm.symbol) {
        this.$message.warning('请先选择合约');
        return;
      }
      
      // 模拟获取行情数据
      const symbolInfo = this.symbolOptions.find(item => item.value === this.orderForm.symbol);
      if (symbolInfo) {
        const name = symbolInfo.label.split(' ')[0];
        const last = (Math.random() * 20 + 10).toFixed(2);
        const preClose = (last * (1 + (Math.random() * 0.1 - 0.05))).toFixed(2);
        const change = (last - preClose).toFixed(2);
        const changePercent = ((change / preClose) * 100).toFixed(2);
        
        this.currentQuote = {
          symbol: this.orderForm.symbol,
          name: name,
          last: parseFloat(last),
          change: parseFloat(change),
          changePercent: parseFloat(changePercent),
          open: parseFloat((preClose * (1 + (Math.random() * 0.02 - 0.01))).toFixed(2)),
          high: parseFloat((last * (1 + Math.random() * 0.05)).toFixed(2)),
          low: parseFloat((last * (1 - Math.random() * 0.05)).toFixed(2)),
          preClose: parseFloat(preClose),
          volume: Math.floor(Math.random() * 10000000),
          turnover: Math.floor(Math.random() * 100000000),
          updateTime: new Date().toLocaleTimeString()
        };
        
        this.$message({
          message: '行情数据已更新',
          type: 'success'
        });
      }
    }
  },
  watch: {
    'orderForm.symbol'(newVal) {
      if (newVal) {
        this.refreshQuote();
      }
    }
  }
}
</script>

<style scoped>
.trading-container {
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
.quote-info {
  padding: 10px;
}
.quote-header {
  text-align: center;
  margin-bottom: 10px;
}
.quote-header h3 {
  margin: 0 0 10px 0;
}
.price {
  font-size: 24px;
  font-weight: bold;
}
.price-up {
  color: #f56c6c;
}
.price-down {
  color: #67c23a;
}
.change {
  font-size: 14px;
  margin-left: 5px;
}
.quote-details {
  margin-top: 10px;
}
.quote-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.label {
  color: #909399;
}
.no-quote {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}
</style>
