<template>
  <div class="backtest-page-container">
    <div class="page-header">
      <h1 class="page-title">策略回测配置</h1>
      <div class="strategy-name" v-if="currentBacktestStrategy">{{ currentBacktestStrategy.name }}</div>
    </div>
    <div class="main-content">
      <el-form :model="backtestConfig" :inline="false" label-width="120px" ref="backtestForm">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合约代码" prop="symbol" :rules="[{ required: true, message: '请输入合约代码', trigger: 'change' }]">
              <el-select
                v-model="backtestConfig.symbol"
                filterable
                remote
                reserve-keyword
                placeholder="请输入合约代码搜索，如 IF2401"
                :remote-method="remoteMethodSymbolSearch"
                :loading="symbolLoading"
                @change="onSymbolChange"
                style="width: 100%;"
                clearable
              >
                <el-option
                  v-for="item in availableSymbols"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="交易所" prop="exchange" :rules="[{ required: true, message: '请选择交易所', trigger: 'change' }]">
              <el-select v-model="backtestConfig.exchange" placeholder="选择交易所" @change="onExchangeChange" style="width: 100%;" filterable clearable>
                <el-option v-for="ex in availableExchanges" :key="ex.value" :label="ex.label" :value="ex.value"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="K线周期" prop="interval" :rules="[{ required: true, message: '请选择K线周期', trigger: 'change' }]">
              <el-select v-model="backtestConfig.interval" placeholder="选择K线周期" @change="onIntervalChange" style="width: 100%;" clearable>
                <el-option v-for="intv in availableIntervals" :key="intv.value" :label="intv.label" :value="intv.value"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="回测模式" prop="mode" :rules="[{ required: true, message: '请选择回测模式', trigger: 'change' }]">
              <el-select v-model="backtestConfig.mode" placeholder="选择回测模式" style="width: 100%;">
                <el-option label="K线 (Bar)" value="bar"></el-option>
                <el-option label="Tick级" value="tick"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date" :rules="[{ required: true, message: '请选择开始日期', trigger: 'change' }]">
              <el-date-picker type="date" placeholder="选择开始日期" v-model="backtestConfig.start_date" style="width: 100%;" format="yyyy-MM-dd" value-format="yyyy-MM-dd"></el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date" :rules="[{ required: true, message: '请选择结束日期', trigger: 'change' }]">
              <el-date-picker type="date" placeholder="选择结束日期" v-model="backtestConfig.end_date" style="width: 100%;" format="yyyy-MM-dd" value-format="yyyy-MM-dd"></el-date-picker>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 数据范围提示将在这里添加 -->
        <el-row :gutter="20" v-if="dataRange.message || (dataRange.startDate && dataRange.endDate)" style="margin-bottom: 10px;">
            <el-col :span="24">
                <el-alert
                    v-if="dataRange.startDate && dataRange.endDate"
                    :title="'提示: 该合约在选定周期下的可用数据范围为 ' + dataRange.startDate + ' 至 ' + dataRange.endDate + (dataRange.count ? ' (共 ' + dataRange.count + ' 条记录)' : '')"
                    type="info"
                    show-icon
                    :closable="false">
                </el-alert>
                <el-alert
                    v-else-if="dataRange.message"
                    :title="dataRange.message"
                    type="warning"
                    show-icon
                    :closable="false">
                </el-alert>
            </el-col>
        </el-row>

        <el-divider content-position="left">策略参数</el-divider>
        <div v-if="currentBacktestStrategy && currentBacktestStrategy.parameters">
          <el-row :gutter="20">
            <el-col :span="12" v-for="(paramDetails, paramName) in currentBacktestStrategy.parameters" :key="paramName">
              <el-form-item :label="paramDetails.description || paramName" :prop="'parameters.' + paramName">
                <el-input-number v-if="paramDetails.type === 'int' || paramDetails.type === 'float'"
                                v-model.number="backtestConfig.parameters[paramName]"
                                :step="paramDetails.type === 'float' ? 0.01 : 1"
                                style="width: 100%;">
                </el-input-number>
                <el-select v-else-if="paramDetails.type === 'enum' && paramDetails.enum_values"
                           v-model="backtestConfig.parameters[paramName]"
                           placeholder="请选择"
                           style="width: 100%;">
                  <el-option v-for="enumValue in paramDetails.enum_values" :key="enumValue" :label="enumValue" :value="enumValue"></el-option>
                </el-select>
                <el-input v-else
                          v-model="backtestConfig.parameters[paramName]"
                          style="width: 100%;">
                </el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <el-divider content-position="left">资金和手续费</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="回测资金" prop="capital">
              <el-input-number v-model="backtestConfig.capital" :min="1000" :step="10000" style="width: 100%;"></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="手续费率" prop="rate">
              <el-input-number v-model="backtestConfig.rate" :precision="5" :step="0.00001" :min="0" style="width: 100%;"></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="滑点(跳)" prop="slippage">
              <el-input-number v-model="backtestConfig.slippage" :min="0" :step="1" style="width: 100%;"></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-actions">
          <el-button type="primary" @click="submitForm('backtestForm')" :loading="submitting" icon="el-icon-video-play" size="medium">开始回测</el-button>
          <el-button @click="resetForm('backtestForm')" icon="el-icon-refresh" size="medium">重置参数</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
// 假设API函数在@/api/strategies中定义
import {
    getStrategyDetail, // 获取策略模板详情
    getUserStrategyDetail, // 获取用户策略详情
    runStrategyBacktest,
    getAvailableExchanges,
    getAvailableSymbols,
    getAvailableIntervals,
    getStockDataRange // 新增的API调用
} from '@/api/strategies';
import { useRouter } from 'vue-router'; // 引入 useRouter

export default {
  name: 'BacktestPageView',
  props: {
    strategyId: { // 从路由参数 /backtest/:strategyId
      type: [String, Number],
      default: null
    }
  },
  data() {
    return {
      currentBacktestStrategy: null, // 将存储加载的策略详情
      backtestConfig: { // 表单v-model绑定的对象
        strategy_id: null,
        strategy_name: '',
        user_id: 1, // 默认用户ID
        symbol: '',
        exchange: '',
        interval: '',
        start_date: '',
        end_date: '',
        initial_capital: 1000000, // 默认初始资金
        rate: 0.0001, // 默认费率 (万分之一)
        slippage: 0, // 默认滑点为0，与后端模型一致
        mode: 'bar', // 默认回测模式 'bar' 或 'tick'
        parameters: {}, // 策略特定参数
      },
      availableExchanges: [], // 用于交易所下拉列表
      availableSymbols: [],   // 用于合约代码下拉列表
      availableIntervals: [], // 用于K线周期下拉列表
      symbolLoading: false,     // 合约代码远程搜索加载状态
      submitting: false,   // 回测执行加载状态
      dataRange: { // 用于存储和显示K线数据范围
        startDate: null,
        endDate: null,
        count: 0,
        message: ''
      },
      allSymbolsCache: [], // 用于缓存从API获取的所有合约，方便本地筛选
      // 其他如回测结果相关的data将在后续步骤添加
    };
  },
  watch: {
    strategyId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.loadStrategyDetails(newId);
        } else {
          // 如果没有strategyId，可能是通用回测，重置策略相关信息
          this.currentBacktestStrategy = null;
          this.backtestConfig.strategy_id = null;
          this.backtestConfig.strategy_name = '';
          this.backtestConfig.parameters = {};
          // 当从有策略切换到无策略时，也重置表单到通用状态
          this.$nextTick(() => {
             if (this.$refs.backtestForm) {
                this.resetForm('backtestForm', false); // false表示不是因为点击重置按钮
             }
          });
        }
      }
    },
    // 监听表单项变化以触发数据范围查询
    'backtestConfig.symbol': 'fetchDataRangeForSelectedStock',
    'backtestConfig.exchange': 'fetchDataRangeForSelectedStock',
    'backtestConfig.interval': 'fetchDataRangeForSelectedStock',
  },
  methods: {
    async loadAvailableExchanges() {
      try {
        const response = await getAvailableExchanges(); // axios response object
        // The actual backend response is in response.data
        if (response.data && response.data.success) {
          if (response.data.data && Array.isArray(response.data.data)) {
            this.availableExchanges = response.data.data.map(ex => ({
              label: `${ex.name} (${ex.value})`,
              value: ex.value
            }));
            if (this.availableExchanges.length === 0) {
              this.$message.info("可用交易所数据为空");
            }
          } else {
            this.availableExchanges = [];
            this.$message.error("加载可用交易所失败: 响应数据格式不正确 (data 字段应为数组)");
          }
        } else {
          // Handles cases where response.data is missing, or response.data.success is false
          this.availableExchanges = [];
          this.$message.error("加载可用交易所失败: " + (response.data && response.data.message ? response.data.message : '未知服务端错误或响应格式不佳'));
        }
      } catch (error) {
        console.error("Error loading exchanges:", error);
        let errorMessage = '加载可用交易所出错 (网络或客户端)';
        if (error.response && error.response.data && error.response.data.message) {
            errorMessage = `加载可用交易所出错: ${error.response.data.message}`;
        } else if (error.message) {
            errorMessage = `加载可用交易所出错: ${error.message}`;
        }
        this.$message.error(errorMessage);
        this.availableExchanges = []; // Fallback
      }
    },
    async remoteMethodSymbolSearch(query) {
      if (query !== '') {
        this.symbolLoading = true;
        try {
          // 优先使用当前选定的交易所进行过滤，如果API支持的话
          const params = { query: query };
          if (this.backtestConfig.exchange) {
            //   params.exchange = this.backtestConfig.exchange; // 如果API支持按交易所过滤
          }
          const response = await getAvailableSymbols(params); // 假设API支持query参数
          if (response.success) {
            // 如果API返回的数据已经按query过滤，则直接使用
            // 否则，如果API返回所有，则前端过滤 (如下面的allSymbolsCache逻辑)
            this.allSymbolsCache = response.data.map(s => ({
                label: `${s.name} (${s.symbol}) - ${s.exchange.toUpperCase()}`,
                value: s.symbol,
                exchange: s.exchange // 保留交易所信息用于可能的自动填充或过滤
            }));

            // 前端基于query再次过滤 (如果API没有完全按query返回)
            // 或者，如果API直接返回过滤后的，就不需要下面这步
            this.availableSymbols = this.allSymbolsCache.filter(s =>
                s.label.toLowerCase().includes(query.toLowerCase()) ||
                s.value.toLowerCase().includes(query.toLowerCase())
            ).slice(0, 100); // 限制下拉列表数量

          } else {
            this.$message.error("搜索合约代码失败: " + (response.message || '未知错误'));
            this.availableSymbols = [];
          }
        } catch (error) {
          console.error("Error searching symbols:", error);
          this.$message.error("搜索合约代码出错");
          this.availableSymbols = [];
        } finally {
          this.symbolLoading = false;
        }
      } else {
        this.availableSymbols = []; // Query为空时清空列表或显示基于交易所的默认列表
      }
    },
    onSymbolChange(symbolValue) {
      console.log('Symbol changed:', symbolValue);
      // 当合约选定后，尝试从缓存或合约数据中找到其交易所信息并自动填充（如果交易所为空）
      if (symbolValue && !this.backtestConfig.exchange) {
        const selectedSymbolData = this.allSymbolsCache.find(s => s.value === symbolValue);
        if (selectedSymbolData && selectedSymbolData.exchange) {
          this.backtestConfig.exchange = selectedSymbolData.exchange;
          // 自动填充交易所会触发 exchange的watch或onExchangeChange，进而刷新周期等
        }
      }
      this.fetchDataRangeForSelectedStock(); // 已通过 watcher 监听，此处可省略或保留作为显式调用
      this.loadAvailableIntervals(); // 根据新的合约和交易所（可能已自动填充）重新加载K线周期
    },
    onExchangeChange(exchangeValue) {
      console.log('Exchange changed:', exchangeValue);
      this.backtestConfig.symbol = ''; // 清空已选合约，因为交易所变了
      this.availableSymbols = [];    // 清空合约下拉列表
      if (exchangeValue) {
          this.loadDefaultSymbolsForExchange(exchangeValue); // 加载新交易所下的默认合约列表
      }
      this.fetchDataRangeForSelectedStock(); // 已通过 watcher 监听
      this.loadAvailableIntervals(); // 根据新的交易所重新加载K线周期
    },
    onIntervalChange(intervalValue) {
      console.log('Interval changed:', intervalValue);
      this.fetchDataRangeForSelectedStock(); // 已通过 watcher 监听
    },
    getIntervalLabel(intervalValue) {
       const map = {
            '1m': '1分钟',
            '5m': '5分钟',
            '15m': '15分钟',
            '30m': '30分钟',
            '1h': '1小时',
            '2h': '2小时',
            '4h': '4小时',
            '1d': '日线',
            '1w': '周线',
            'tick': 'Tick级'
        };
        return map[intervalValue] || intervalValue;
    },
    async fetchDataRangeForSelectedStock() {
        if (!this.backtestConfig.symbol || !this.backtestConfig.exchange || !this.backtestConfig.interval) {
            // console.log('Skipping data range fetch: not all params are set.');
            // Clear previous message if user is clearing selections, but only if it's not already a specific error
            if (this.dataRange.message !== '正在查询数据范围...') { // Avoid clearing if a fetch is in progress
                // this.dataRange.message = '请选择合约、交易所和K线周期以获取数据范围。';
            }
            this.dataRange.startDate = null; // Clear dates if params are incomplete
            this.dataRange.endDate = null;
            this.dataRange.count = 0;
            // Also clear from backtestConfig if they were auto-filled
            // this.backtestConfig.start_date = null;
            // this.backtestConfig.end_date = null;
            return;
        }
        this.dataRange.message = '正在查询数据范围...';
        try {
            const axiosResponse = await getStockDataRange({
                symbol: this.backtestConfig.symbol,
                exchange: this.backtestConfig.exchange,
                interval: this.backtestConfig.interval
            });

            const serverResponse = axiosResponse.data; // Key: actual server JSON payload

            if (serverResponse && serverResponse.success === true && serverResponse.data &&
                typeof serverResponse.data.start_date === 'string' && serverResponse.data.start_date.trim() !== '' &&
                typeof serverResponse.data.end_date === 'string' && serverResponse.data.end_date.trim() !== '') {

                this.dataRange.startDate = serverResponse.data.start_date;
                this.dataRange.endDate = serverResponse.data.end_date;
                this.dataRange.count = serverResponse.data.count;
                this.dataRange.message = ''; // Clear warning message, hides the alert

                // Update form model, which should update date pickers
                this.backtestConfig.start_date = serverResponse.data.start_date;
                this.backtestConfig.end_date = serverResponse.data.end_date;

                // console.log('Successfully processed data range. Dates set in backtestConfig to:', this.backtestConfig.start_date, 'to', this.backtestConfig.end_date);
            } else {
                this.dataRange.startDate = null;
                this.dataRange.endDate = null;
                this.dataRange.count = 0;
                let errMsg = '未能获取该合约的数据范围。';

                if (serverResponse && serverResponse.message) {
                    errMsg = serverResponse.message; // Use message from server if available
                } else if (axiosResponse && axiosResponse.status && axiosResponse.status !== 200) {
                    errMsg = `请求数据范围失败，状态码: ${axiosResponse.status}`;
                } else if (axiosResponse && !serverResponse && axiosResponse.status === 200) {
                     errMsg = '请求数据范围成功，但服务器未返回有效或可解析的数据。';
                } else if (serverResponse && serverResponse.success === true && serverResponse.data) {
                    if (!serverResponse.data.start_date || typeof serverResponse.data.start_date !== 'string' || serverResponse.data.start_date.trim() === '') {
                        errMsg = '服务器返回数据不完整 (起始日期缺失或格式无效)。';
                    } else if (!serverResponse.data.end_date || typeof serverResponse.data.end_date !== 'string' || serverResponse.data.end_date.trim() === '') {
                        errMsg = '服务器返回数据不完整 (结束日期缺失或格式无效)。';
                    }
                } else if (serverResponse && serverResponse.success === false) {
                    errMsg = serverResponse.message || '服务器明确表示获取数据范围失败。';
                } else if (typeof serverResponse !== 'object' || serverResponse === null) {
                     errMsg = `服务器响应格式意外: 收到的类型是 ${typeof serverResponse}。`;
                }

                this.dataRange.message = errMsg;
                console.error('Failed to process data range. Error Message:', this.dataRange.message, 'Raw serverResponse:', JSON.stringify(serverResponse, null, 2));
            }
        } catch (error) {
            console.error('Exception caught in fetchDataRangeForSelectedStock:', error.message, error.stack, error.response ? JSON.stringify(error.response.data) : '');
            this.dataRange.startDate = null;
            this.dataRange.endDate = null;
            this.dataRange.count = 0;
            let detailedErrorMsg = '查询数据范围时发生客户端代码异常。';
            if (error.response && error.response.data && error.response.data.message) {
                detailedErrorMsg = `服务器错误: ${error.response.data.message}`;
            } else if (error.response && error.response.status) {
                detailedErrorMsg = `服务器请求错误，状态码: ${error.response.status}`;
            } else if (error.message) {
                detailedErrorMsg = error.message;
            }
            this.dataRange.message = detailedErrorMsg;
        }
    },

    async loadStrategyDetails(strategyId, isParameterReset = false) {
      if (!strategyId) return;
      try {
        this.submitting = true; // 使用 submitting 状态

        // 先尝试获取用户策略详情
        let response;
        let isUserStrategy = false;

        try {
          console.log('尝试获取用户策略详情:', strategyId);
          response = await getUserStrategyDetail(strategyId);
          if (response.data && response.data.success && response.data.data) {
            isUserStrategy = true;
            console.log('成功获取用户策略详情:', response.data.data);
          }
        } catch (userStrategyErr) {
          console.log('获取用户策略详情失败，尝试获取策略模板:', userStrategyErr);
          // 如果获取用户策略失败，尝试获取策略模板
          response = await getStrategyDetail(strategyId);
        }

        if (response.data && response.data.success && response.data.data) {
          this.currentBacktestStrategy = response.data.data; // 存储完整策略对象

          if (!isParameterReset) { // 首次加载或非参数重置
            // 如果是用户策略，使用strategy_id字段，否则使用id字段
            this.backtestConfig.strategy_id = isUserStrategy ? response.data.data.strategy_id : response.data.data.id;
            this.backtestConfig.strategy_name = response.data.data.name;
            // 可以考虑将策略的默认交易对、周期等也加载进来，如果API提供
            // this.backtestConfig.symbol = response.data.default_symbol || '';
            // this.backtestConfig.exchange = response.data.default_exchange || '';
            // this.backtestConfig.interval = response.data.default_interval || '';
          }

          // 总是（重新）加载策略的默认参数
          const newParameters = {};
          // 如果是用户策略，使用parameters字段，如果是策略模板，使用parameters字段的default值
          if (isUserStrategy && response.data.data.parameters) {
            // 用户策略的参数已经是具体值，直接使用
            this.backtestConfig.parameters = response.data.data.parameters;
          } else if (response.data.data.parameters) {
            // 策略模板的参数是参数定义，需要提取default值
            for (const paramName in response.data.data.parameters) {
              newParameters[paramName] = response.data.data.parameters[paramName].default;
            }
            this.backtestConfig.parameters = newParameters;
          }

          // 如果加载了策略，可能需要重新获取数据范围
          // 但这通常由 symbol/exchange/interval 的 watcher 触发
          // 如果策略有默认的symbol/exchange/interval，则会自动触发

        } else {
          this.$message.error(`加载策略详情失败: ${response.message || '未知错误'}`);
          this.currentBacktestStrategy = null;
          this.backtestConfig.strategy_id = null;
          this.backtestConfig.strategy_name = '';
          this.backtestConfig.parameters = {};
        }
      } catch (error) {
        console.error("Error loading strategy details:", error);
        this.$message.error("加载策略详情时发生客户端错误");
        this.currentBacktestStrategy = null;
      } finally {
        this.submitting = false;
      }
    },
    async submitForm(formName) {
      this.$refs[formName].validate(async (valid) => {
        if (valid) {
          this.submitting = true;
          try {
            // 构建API需要的payload
            const payload = {
              strategy_id: this.backtestConfig.strategy_id,
              name: this.backtestConfig.strategy_name,
              user_id: this.backtestConfig.user_id,
              symbol: this.backtestConfig.symbol,
              exchange: this.backtestConfig.exchange,
              interval: this.backtestConfig.interval,
              start_date: this.backtestConfig.start_date,
              end_date: this.backtestConfig.end_date,
              initial_capital: this.backtestConfig.initial_capital,
              rate: this.backtestConfig.rate,
              slippage: this.backtestConfig.slippage,
              mode: this.backtestConfig.mode,
              parameters: this.backtestConfig.parameters || {},
            };

            console.log('Submitting backtest with payload:', payload);

            // 直接从控制台获取回测ID
            console.log('\n\n\n请在控制台中查找回测ID，格式如: "record_id": 123\n\n\n');

            const axiosResponse = await runStrategyBacktest(payload);

            const serverResponse = axiosResponse.data; // serverResponse is the actual JSON from the server

            console.log('收到服务器响应:', serverResponse);
            console.log('响应类型:', typeof serverResponse);
            console.log('响应结构 (JSON字符串):', JSON.stringify(serverResponse));
            console.log('响应数据类型:', typeof serverResponse.data);
            console.log('响应数据键:', Object.keys(serverResponse.data));

            // 深度检查响应结构
            if (serverResponse.data && typeof serverResponse.data === 'object') {
              console.log('数据对象内容:', serverResponse.data);

              if (serverResponse.data.statistics) {
                console.log('统计数据内容:', serverResponse.data.statistics);
              }

              // 递归查找所有可能的 ID 字段
              const findAllIds = (obj, path = '') => {
                if (!obj || typeof obj !== 'object') return;

                Object.keys(obj).forEach(key => {
                  const newPath = path ? `${path}.${key}` : key;
                  if (key === 'id' || key === 'record_id' || key.includes('id')) {
                    console.log(`找到可能的ID字段: ${newPath} = ${obj[key]}`);
                  }

                  if (obj[key] && typeof obj[key] === 'object') {
                    findAllIds(obj[key], newPath);
                  }
                });
              };

              findAllIds(serverResponse);
            }
            console.log('Response type:', typeof serverResponse);
            console.log('Response structure:', JSON.stringify(serverResponse, null, 2));

            // 详细检查响应结构
            if (serverResponse.data) {
              console.log('data field type:', typeof serverResponse.data);
              console.log('data field keys:', Object.keys(serverResponse.data));

              // 如果 data 是对象，递归检查其所有属性
              const inspectObject = (obj, path = '') => {
                if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
                  Object.keys(obj).forEach(key => {
                    const newPath = path ? `${path}.${key}` : key;
                    console.log(`Checking path: ${newPath}, value:`, obj[key]);
                    inspectObject(obj[key], newPath);
                  });
                }
              };

              inspectObject(serverResponse.data);
            }

            if (serverResponse.success && serverResponse.data) {
              this.$message.success(serverResponse.message || '回测任务已启动！');

              // 检查不同的响应格式，尝试找到回测ID
              let recordId = null;

              // 直接使用回测结果中的回测ID
              if (serverResponse.data && serverResponse.data.statistics) {
                // 从统计数据中提取回测ID
                const stats = serverResponse.data.statistics;

                // 尝试从统计数据中获取回测ID
                if (stats.record_id) {
                  recordId = stats.record_id;
                  console.log('从统计数据中找到回测ID (statistics.record_id):', recordId);
                } else if (stats.id) {
                  recordId = stats.id;
                  console.log('从统计数据中找到回测ID (statistics.id):', recordId);
                }
              }

              // 如果还是找不到，尝试从响应中提取数字字符串
              if (!recordId) {
                const responseStr = JSON.stringify(serverResponse);
                const matches = responseStr.match(/"id":\s*(\d+)/g) || responseStr.match(/"record_id":\s*(\d+)/g);
                if (matches && matches.length > 0) {
                  const idMatch = matches[0].match(/(\d+)/);
                  if (idMatch && idMatch[0]) {
                    recordId = idMatch[0];
                    console.log('从响应字符串中提取到回测ID:', recordId);
                  }
                }
              }

              // 不使用临时ID，如果找不到就显示错误信息

              if (recordId) {
                this.$router.push({ name: 'BacktestReport', params: { backtest_id: recordId } });
              } else {
                console.error("成功响应中未找到回测ID:", serverResponse);

                // 使用 Element UI 的 MessageBox 请求用户手动输入回测ID
                this.$confirm('系统无法自动获取回测ID，请从控制台中查找回测ID并手动输入。是否要手动输入回测ID？', '提示', {
                  confirmButtonText: '是，我要手动输入',
                  cancelButtonText: '取消',
                  type: 'warning'
                }).then(() => {
                  // 用户点击确认按钮，显示输入框
                  this.$prompt('请输入回测ID', '手动输入回测ID', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    inputPattern: /^\d+$/,
                    inputErrorMessage: '回测ID必须是数字'
                  }).then(({ value }) => {
                    // 用户输入了回测ID，跳转到报告页面
                    this.$router.push({ name: 'BacktestReport', params: { backtest_id: value } });
                  }).catch(() => {
                    this.$message.info('已取消手动输入');
                  });
                }).catch(() => {
                  this.$message.info('已取消手动输入');
                });
              }
            } else {
              // Handle various error scenarios based on outer and inner success flags
              let errorMessage = '回测请求失败或返回无效数据';
              if (serverResponse && !serverResponse.success && serverResponse.message) { // Outer success is false
                  errorMessage = serverResponse.message;
              } else if (serverResponse && serverResponse.data && serverResponse.data.message) { // Inner error message or general message if inner success is false
                  errorMessage = serverResponse.data.message;
              } else if (serverResponse && serverResponse.message) { // Fallback to outer message
                  errorMessage = serverResponse.message;
              }
              this.$message.error(errorMessage);
              console.error('回测请求失败:', serverResponse);
            }
          } catch (error) {
            console.error('执行回测时出错:', error);
            let detailMessage = '请检查网络连接或联系管理员。';
            if (error.response && error.response.data && error.response.data.message) {
                detailMessage = error.response.data.message;
            } else if (error.message) {
                detailMessage = error.message;
            }
            this.$message.error(`回测请求异常: ${detailMessage}`);
          } finally {
            this.submitting = false;
          }
        } else {
          this.$message.error('请填写所有必填项');
          return false;
        }
      });
    },
    resetForm(formName, triggeredByButton = true) {
      this.dataRange = { startDate: null, endDate: null, count: 0, message: '' };
      if (this.currentBacktestStrategy && triggeredByButton) {
          // 如果有策略上下文，并且是用户点击重置按钮，则重载策略的默认参数
          this.loadStrategyDetails(this.currentBacktestStrategy.id, true);
          // 保留 symbol, exchange, interval 等，只重置参数和日期等
          // 日期等非策略特定参数也应该重置为默认
          const today = new Date();
          const oneYearAgo = new Date(new Date().setFullYear(today.getFullYear() - 1));
          this.backtestConfig.start_date = oneYearAgo.toISOString().split('T')[0];
          this.backtestConfig.end_date = today.toISOString().split('T')[0];
          this.backtestConfig.initial_capital = 1000000;
          this.backtestConfig.rate = 0.0001;
          this.backtestConfig.slippage = 0;
          this.backtestConfig.mode = 'bar';
          // 表单验证状态也需要重置
          this.$refs[formName].clearValidate();
      } else {
          // 无策略上下文，或非按钮触发的重置 (例如从有策略切换到无策略时)
          if (this.$refs[formName]) this.$refs[formName].resetFields();

          // 手动重置非prop绑定的字段，以及resetFields可能未覆盖的
          const today = new Date();
          const oneYearAgo = new Date(new Date().setFullYear(today.getFullYear() - 1));
          this.backtestConfig.start_date = oneYearAgo.toISOString().split('T')[0];
          this.backtestConfig.end_date = today.toISOString().split('T')[0];
          this.backtestConfig.initial_capital = 1000000;
          this.backtestConfig.rate = 0.0001;
          this.backtestConfig.slippage = 0;
          this.backtestConfig.mode = 'bar';
          this.backtestConfig.strategy_id = null;
          this.backtestConfig.strategy_name = '';
          this.backtestConfig.parameters = {};
      }
    },
    async loadAvailableIntervals() {
      try {
        const params = {};
        if (this.backtestConfig.exchange) params.exchange = this.backtestConfig.exchange;
        if (this.backtestConfig.symbol) params.symbol = this.backtestConfig.symbol;

        const axiosResponse = await getAvailableIntervals(params);

        if (axiosResponse.data && axiosResponse.data.success) {
          if (Array.isArray(axiosResponse.data.data)) {
            this.availableIntervals = axiosResponse.data.data.map(item => ({
              value: item.value,
              label: item.label || this.getIntervalLabel(item.value)
            }));
            if (axiosResponse.data.data.length === 0) {
              this.$message.info('K线周期数据为空');
            }
          } else {
            console.error('加载K线周期失败: response.data.data is not an array', axiosResponse.data);
            this.$message.error('加载K线周期失败: 后端响应数据格式不正确 (data应为数组)');
            this.availableIntervals = this.getDefaultIntervals();
          }
        } else {
          const errorMessage = axiosResponse.data ? axiosResponse.data.message : '未知服务端错误';
          this.$message.error("加载K线周期失败: " + errorMessage);
          this.availableIntervals = this.getDefaultIntervals();
        }
      } catch (error) {
        console.error("Exception during loadAvailableIntervals:", error);
        let displayError = "加载K线周期出错 (详细请看控制台)";
        if (error.response && error.response.data) {
            if (error.response.data.message) {
                 displayError = `加载K线周期出错: ${error.response.data.message}`;
            } else if (error.response.data.detail){
                 displayError = `加载K线周期出错: ${error.response.data.detail}`;
                 if (typeof error.response.data.detail === 'object' && error.response.data.detail[0] && error.response.data.detail[0].msg) {
                    displayError = `加载K线周期出错: ${error.response.data.detail[0].msg} (字段: ${error.response.data.detail[0].loc.join('.')})`;
                 }
            }
        } else if (error.message) {
            displayError = `加载K线周期出错: ${error.message}`;
        }
        this.$message.error(displayError);
        this.availableIntervals = this.getDefaultIntervals();
      }
    },
    getDefaultIntervals() {
        return [
            { value: '1m', label: '1分钟' },
            { value: '5m', label: '5分钟' },
            { value: '1h', label: '1小时' },
            { value: '1d', label: '日线' }
        ];
    },
    async loadDefaultSymbolsForExchange(exchange) {
        // 当交易所选定，但合约搜索框为空时，可以加载该交易所下的默认合约列表
        if (!exchange) {
            this.availableSymbols = [];
            return;
        }
        this.symbolLoading = true;
        try {
            // getAvailableSymbols返回的是axiosResponse，所以需要从中取data
            const axiosFullResponse = await getAvailableSymbols({ exchange: exchange });
            const response = axiosFullResponse.data; // 服务器的实际响应体

            if (response && response.success) {
                if (Array.isArray(response.data)) {
                    this.availableSymbols = response.data.map(s => ({
                        label: `${s.name} (${s.symbol}) - ${s.exchange.toUpperCase()}`,
                        value: s.symbol,
                        exchange: s.exchange
                    })).slice(0, 100); // 限制数量，避免过多DOM
                    this.allSymbolsCache = [...this.availableSymbols];
                    if (response.data.length === 0) {
                        this.$message.info(`交易所 ${exchange} 下没有找到合约数据`);
                    }
                } else {
                    console.error("Error loading symbols: response.data.data is not an array", response);
                    this.$message.error("加载合约列表失败: 后端响应数据格式不正确 (data应为数组)");
                    this.availableSymbols = [];
                }
            } else {
                const errorMessage = (response && response.message) ? response.message : '未知服务端错误';
                this.$message.error("加载合约列表失败: " + errorMessage);
                this.availableSymbols = [];
            }
        } catch (error) {
            console.error("Exception during loadDefaultSymbolsForExchange for exchange:", exchange, error);
            let displayError = "加载合约列表出错 (详细请看控制台)";
            if (error.response && error.response.data) {
                if (error.response.data.message) {
                     displayError = `加载合约列表出错: ${error.response.data.message}`;
                } else if (error.response.data.detail){
                     displayError = `加载合约列表出错: ${error.response.data.detail}`;
                     if (typeof error.response.data.detail === 'object' && error.response.data.detail[0] && error.response.data.detail[0].msg) {
                        displayError = `加载合约列表出错: ${error.response.data.detail[0].msg} (字段: ${error.response.data.detail[0].loc.join('.')})`;
                     }
                }
            } else if (error.message) {
                displayError = `加载合约列表出错: ${error.message}`;
            }
            this.$message.error(displayError);
            this.availableSymbols = [];
        } finally {
            this.symbolLoading = false;
        }
    },
  },
  created() {
    if (this.strategyId) {
      this.loadStrategyDetails(this.strategyId);
      console.log('Strategy ID from route:', this.strategyId);
    } else {
        // 设置默认日期范围 (如果不是从特定策略进入)
        const today = new Date();
        const oneYearAgo = new Date(new Date().setFullYear(today.getFullYear() - 1));
        this.backtestConfig.start_date = oneYearAgo.toISOString().split('T')[0];
        this.backtestConfig.end_date = today.toISOString().split('T')[0];
    }

    this.loadAvailableExchanges();
    this.loadAvailableIntervals(); // 加载通用的周期列表，或在交易所/合约选定后再次加载
    // 考虑是否在created时加载一个默认的合约列表，或者等待用户输入
    // this.loadDefaultSymbolsForExchange(null); // 初始不加载特定交易所的合约
  }
};
</script>

<style scoped>
/* 整体布局 */
.backtest-page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-lg);
  background-color: var(--bg-white);
}

/* 页面标题 */
.page-header {
  margin-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: var(--spacing-sm);
}

.page-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xxs) 0;
}

.strategy-name {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

/* 主内容区 */
.main-content {
  background-color: var(--bg-white);
}

/* 表单样式 */
.el-form {
  margin-bottom: var(--spacing-lg);
}

.el-form-item {
  margin-bottom: var(--spacing-md);
}

.el-form-item :deep(.el-form-item__label) {
  color: var(--text-primary);
  font-weight: var(--font-weight-normal);
}

.el-select, .el-input, .el-input-number, .el-date-picker {
  width: 100%;
}

/* 分隔线 */
.el-divider {
  margin: var(--spacing-lg) 0;
}

.el-divider :deep(.el-divider__text) {
  background-color: var(--bg-white);
  color: var(--text-primary);
  font-weight: var(--font-weight-normal);
  font-size: var(--font-size-sm);
}

/* 按钮区域 */
.form-actions {
  margin-top: var(--spacing-xl);
  text-align: center;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-color);
}

.form-actions .el-button {
  min-width: 120px;
}

.form-actions .el-button + .el-button {
  margin-left: var(--spacing-md);
}

/* 提示信息 */
.el-alert {
  margin-bottom: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .backtest-page-container {
    padding: var(--spacing-sm);
  }

  .page-header {
    margin-bottom: var(--spacing-md);
  }

  .form-actions .el-button {
    min-width: 100px;
  }
}
</style>
