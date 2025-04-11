<template>
  <div class="ai-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>AI分析</span>
          </div>
          
          <el-form :inline="true" :model="analysisForm" class="analysis-form">
            <el-form-item label="分析类型">
              <el-select v-model="analysisForm.type" placeholder="请选择分析类型">
                <el-option label="市场情绪分析" value="sentiment"></el-option>
                <el-option label="趋势预测" value="trend"></el-option>
                <el-option label="技术指标分析" value="technical"></el-option>
                <el-option label="基本面分析" value="fundamental"></el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="交易品种">
              <el-select v-model="analysisForm.symbol" placeholder="请选择交易品种" filterable>
                <el-option
                  v-for="item in symbolOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value">
                </el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="analysisForm.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="yyyy-MM-dd"
                value-format="yyyy-MM-dd">
              </el-date-picker>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="runAnalysis">开始分析</el-button>
            </el-form-item>
          </el-form>
          
          <div v-loading="analysisLoading">
            <div v-if="showResult" class="analysis-result">
              <el-divider content-position="left">分析结果</el-divider>
              
              <div class="result-header">
                <h3>{{ getAnalysisTitle() }}</h3>
                <p class="result-date">分析时间: {{ new Date().toLocaleString() }}</p>
              </div>
              
              <div class="result-summary">
                <div class="summary-card" :class="getResultClass()">
                  <div class="summary-icon">
                    <i :class="getResultIcon()"></i>
                  </div>
                  <div class="summary-content">
                    <div class="summary-title">{{ getResultTitle() }}</div>
                    <div class="summary-description">{{ getResultDescription() }}</div>
                  </div>
                </div>
              </div>
              
              <div class="result-details">
                <el-collapse v-model="activeNames">
                  <el-collapse-item title="详细分析" name="1">
                    <div class="detail-content">
                      <p>{{ analysisResult.details }}</p>
                    </div>
                  </el-collapse-item>
                  <el-collapse-item title="技术指标" name="2">
                    <div class="indicators">
                      <el-row :gutter="20">
                        <el-col :span="8" v-for="(indicator, index) in analysisResult.indicators" :key="index">
                          <div class="indicator-item">
                            <div class="indicator-name">{{ indicator.name }}</div>
                            <div class="indicator-value">{{ indicator.value }}</div>
                            <div :class="['indicator-signal', indicator.signal]">
                              {{ getSignalText(indicator.signal) }}
                            </div>
                          </div>
                        </el-col>
                      </el-row>
                    </div>
                  </el-collapse-item>
                  <el-collapse-item title="预测趋势" name="3">
                    <div class="prediction">
                      <div class="prediction-chart">
                        <div id="prediction-chart" class="chart-container"></div>
                      </div>
                      <div class="prediction-text">
                        <p>{{ analysisResult.prediction }}</p>
                      </div>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
            <div v-else class="no-result">
              <p>请选择分析类型和交易品种，然后点击"开始分析"按钮</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>AI助手</span>
          </div>
          
          <div class="ai-assistant">
            <div class="chat-container">
              <div class="chat-messages" ref="chatMessages">
                <div v-for="(message, index) in chatMessages" :key="index" :class="['message', message.type]">
                  <div class="message-avatar">
                    <i :class="message.type === 'assistant' ? 'el-icon-s-platform' : 'el-icon-user'"></i>
                  </div>
                  <div class="message-content">
                    <div class="message-text">{{ message.content }}</div>
                    <div class="message-time">{{ message.time }}</div>
                  </div>
                </div>
              </div>
              
              <div class="chat-input">
                <el-input
                  v-model="userInput"
                  placeholder="输入您的问题..."
                  @keyup.enter.native="sendMessage">
                  <el-button slot="append" icon="el-icon-s-promotion" @click="sendMessage"></el-button>
                </el-input>
              </div>
            </div>
            
            <div class="assistant-suggestions">
              <p>您可以询问:</p>
              <el-button
                v-for="(suggestion, index) in suggestions"
                :key="index"
                size="small"
                @click="useSuggestion(suggestion)">
                {{ suggestion }}
              </el-button>
            </div>
          </div>
        </el-card>
        
        <el-card class="box-card" style="margin-top: 20px;">
          <div slot="header" class="clearfix">
            <span>市场热点</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="refreshHotTopics">刷新</el-button>
          </div>
          
          <div v-loading="topicsLoading">
            <div class="hot-topics">
              <div v-for="(topic, index) in hotTopics" :key="index" class="topic-item">
                <div class="topic-rank">{{ index + 1 }}</div>
                <div class="topic-content">
                  <div class="topic-title">{{ topic.title }}</div>
                  <div class="topic-stats">
                    <span class="topic-heat">
                      <i class="el-icon-hot-water"></i> {{ topic.heat }}
                    </span>
                    <span class="topic-sentiment" :class="topic.sentiment">
                      <i :class="getSentimentIcon(topic.sentiment)"></i> {{ getSentimentText(topic.sentiment) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'AI',
  data() {
    return {
      analysisForm: {
        type: 'sentiment',
        symbol: '',
        dateRange: []
      },
      symbolOptions: [
        { value: '600000', label: '浦发银行 (600000)' },
        { value: '601398', label: '工商银行 (601398)' },
        { value: '000001', label: '平安银行 (000001)' },
        { value: '000858', label: '五粮液 (000858)' },
        { value: 'IF2106', label: '沪深300期货 (IF2106)' }
      ],
      analysisLoading: false,
      showResult: false,
      activeNames: ['1', '2', '3'],
      analysisResult: {
        type: 'sentiment',
        symbol: '600000',
        name: '浦发银行',
        result: 'positive',
        score: 75,
        details: '根据对近期市场数据的分析，浦发银行(600000)整体市场情绪偏向积极。社交媒体情绪分析显示，投资者对该股票的讨论中积极情绪占比约75%，负面情绪占比约15%，中性情绪占比约10%。技术指标方面，MACD指标显示多头趋势，RSI指标处于60左右，表明市场处于适度买入区间。结合基本面数据，该股票近期业绩表现稳定，市场预期较为乐观。',
        indicators: [
          { name: 'MACD', value: '0.25', signal: 'buy' },
          { name: 'RSI', value: '60.5', signal: 'neutral' },
          { name: 'KDJ', value: 'K:75.3 D:65.2 J:85.4', signal: 'buy' },
          { name: 'MA', value: 'MA5>MA10>MA20', signal: 'buy' },
          { name: 'BOLL', value: '上轨:11.25 中轨:10.50 下轨:9.75', signal: 'neutral' },
          { name: 'VOL', value: '较前一交易日增加15%', signal: 'buy' }
        ],
        prediction: '基于历史数据和当前市场情绪，AI模型预测浦发银行(600000)未来5个交易日可能呈现震荡上行趋势，预计价格区间在10.25-11.50元之间，上涨概率约为65%。建议投资者关注市场整体走势和行业政策变化，适时调整持仓策略。'
      },
      userInput: '',
      chatMessages: [
        {
          type: 'assistant',
          content: '您好！我是SimpleTrade的AI助手，有什么可以帮您的吗？',
          time: '刚刚'
        }
      ],
      suggestions: [
        '如何解读MACD指标？',
        '什么是KDJ指标？',
        '如何判断市场趋势？',
        '如何使用AI分析功能？'
      ],
      topicsLoading: false,
      hotTopics: [
        { title: '央行降准对银行股的影响', heat: 9865, sentiment: 'positive' },
        { title: '科技股回调是否是买入机会', heat: 8754, sentiment: 'neutral' },
        { title: '新能源汽车销量持续增长', heat: 7632, sentiment: 'positive' },
        { title: '地产股持续低迷', heat: 6543, sentiment: 'negative' },
        { title: '医药板块业绩分化', heat: 5421, sentiment: 'neutral' }
      ]
    }
  },
  methods: {
    runAnalysis() {
      if (!this.analysisForm.symbol) {
        this.$message.warning('请选择交易品种');
        return;
      }
      
      this.analysisLoading = true;
      
      // 模拟API请求
      setTimeout(() => {
        this.analysisLoading = false;
        this.showResult = true;
        this.$message.success('分析完成');
        
        // 更新分析结果
        const symbolInfo = this.symbolOptions.find(item => item.value === this.analysisForm.symbol);
        if (symbolInfo) {
          this.analysisResult.symbol = this.analysisForm.symbol;
          this.analysisResult.name = symbolInfo.label.split(' ')[0];
          this.analysisResult.type = this.analysisForm.type;
        }
        
        // 在实际项目中，这里应该初始化图表
        this.$nextTick(() => {
          this.initChart();
        });
      }, 2000);
    },
    getAnalysisTitle() {
      const typeMap = {
        sentiment: '市场情绪分析',
        trend: '趋势预测',
        technical: '技术指标分析',
        fundamental: '基本面分析'
      };
      return `${this.analysisResult.name} (${this.analysisResult.symbol}) - ${typeMap[this.analysisResult.type]}`;
    },
    getResultClass() {
      return `result-${this.analysisResult.result}`;
    },
    getResultIcon() {
      const iconMap = {
        positive: 'el-icon-top',
        neutral: 'el-icon-right',
        negative: 'el-icon-bottom'
      };
      return iconMap[this.analysisResult.result];
    },
    getResultTitle() {
      const titleMap = {
        positive: '看涨信号',
        neutral: '中性信号',
        negative: '看跌信号'
      };
      return titleMap[this.analysisResult.result];
    },
    getResultDescription() {
      const descMap = {
        positive: `AI分析显示积极情绪占比${this.analysisResult.score}%，建议关注买入机会。`,
        neutral: `AI分析显示市场情绪中性，积极情绪占比${this.analysisResult.score}%，建议观望。`,
        negative: `AI分析显示负面情绪占比${100 - this.analysisResult.score}%，建议谨慎操作。`
      };
      return descMap[this.analysisResult.result];
    },
    getSignalText(signal) {
      const signalMap = {
        buy: '买入',
        sell: '卖出',
        neutral: '中性'
      };
      return signalMap[signal];
    },
    initChart() {
      // 在实际项目中，这里应该使用ECharts或其他图表库初始化图表
      console.log('初始化图表');
    },
    sendMessage() {
      if (!this.userInput.trim()) return;
      
      // 添加用户消息
      this.chatMessages.push({
        type: 'user',
        content: this.userInput,
        time: '刚刚'
      });
      
      const userQuestion = this.userInput;
      this.userInput = '';
      
      // 滚动到底部
      this.$nextTick(() => {
        const container = this.$refs.chatMessages;
        container.scrollTop = container.scrollHeight;
      });
      
      // 模拟AI回复
      setTimeout(() => {
        let response = '';
        
        if (userQuestion.includes('MACD')) {
          response = 'MACD(Moving Average Convergence Divergence)是一种趋势跟踪的动量指标，用于显示两条移动平均线之间的关系。当MACD线上穿信号线时，通常被视为买入信号；当MACD线下穿信号线时，通常被视为卖出信号。';
        } else if (userQuestion.includes('KDJ')) {
          response = 'KDJ指标是一种超买超卖指标，由K线、D线和J线组成。当K线上穿D线时，通常被视为买入信号；当K线下穿D线时，通常被视为卖出信号。J线则可以用来判断市场的超买超卖状态。';
        } else if (userQuestion.includes('趋势')) {
          response = '判断市场趋势可以使用多种技术指标，如移动平均线、MACD、趋势线等。一般来说，当价格位于上升趋势中时，价格会创造更高的高点和更高的低点；当价格位于下降趋势中时，价格会创造更低的高点和更低的低点。';
        } else if (userQuestion.includes('AI分析')) {
          response = '使用AI分析功能很简单：1. 选择分析类型（市场情绪、趋势预测等）；2. 选择交易品种；3. 设置时间范围；4. 点击"开始分析"按钮。系统会自动分析数据并生成报告。';
        } else {
          response = '感谢您的提问。我们的AI系统正在分析您的问题，将尽快为您提供更准确的回答。您也可以尝试点击下方的建议问题，或者提出更具体的问题。';
        }
        
        this.chatMessages.push({
          type: 'assistant',
          content: response,
          time: '刚刚'
        });
        
        // 滚动到底部
        this.$nextTick(() => {
          const container = this.$refs.chatMessages;
          container.scrollTop = container.scrollHeight;
        });
      }, 1000);
    },
    useSuggestion(suggestion) {
      this.userInput = suggestion;
      this.sendMessage();
    },
    refreshHotTopics() {
      this.topicsLoading = true;
      
      // 模拟API请求
      setTimeout(() => {
        this.topicsLoading = false;
        this.$message.success('热点话题已更新');
      }, 1000);
    },
    getSentimentIcon(sentiment) {
      const iconMap = {
        positive: 'el-icon-top',
        neutral: 'el-icon-right',
        negative: 'el-icon-bottom'
      };
      return iconMap[sentiment];
    },
    getSentimentText(sentiment) {
      const textMap = {
        positive: '看涨',
        neutral: '中性',
        negative: '看跌'
      };
      return textMap[sentiment];
    }
  }
}
</script>

<style scoped>
.ai-container {
  padding: 20px;
}
.analysis-form {
  margin-bottom: 20px;
}
.no-result {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}
.result-header {
  margin-bottom: 20px;
}
.result-header h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #303133;
}
.result-date {
  color: #909399;
  font-size: 14px;
}
.summary-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}
.result-positive {
  background-color: rgba(245, 108, 108, 0.1);
  border-left: 4px solid #f56c6c;
}
.result-neutral {
  background-color: rgba(144, 147, 153, 0.1);
  border-left: 4px solid #909399;
}
.result-negative {
  background-color: rgba(103, 194, 58, 0.1);
  border-left: 4px solid #67c23a;
}
.summary-icon {
  font-size: 36px;
  margin-right: 20px;
}
.result-positive .summary-icon {
  color: #f56c6c;
}
.result-neutral .summary-icon {
  color: #909399;
}
.result-negative .summary-icon {
  color: #67c23a;
}
.summary-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
}
.summary-description {
  color: #606266;
}
.detail-content {
  line-height: 1.6;
  color: #606266;
}
.indicators {
  margin-top: 10px;
}
.indicator-item {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
}
.indicator-name {
  font-weight: bold;
  margin-bottom: 5px;
}
.indicator-value {
  color: #606266;
  margin-bottom: 5px;
}
.indicator-signal {
  font-size: 14px;
  font-weight: bold;
}
.buy {
  color: #f56c6c;
}
.sell {
  color: #67c23a;
}
.neutral {
  color: #909399;
}
.prediction-chart {
  height: 300px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}
.prediction-text {
  line-height: 1.6;
  color: #606266;
}
.chat-container {
  height: 300px;
  display: flex;
  flex-direction: column;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  margin-bottom: 10px;
}
.message {
  display: flex;
  margin-bottom: 15px;
}
.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-size: 18px;
}
.assistant .message-avatar {
  background-color: #409EFF;
  color: #fff;
}
.user .message-avatar {
  background-color: #67c23a;
  color: #fff;
}
.message-content {
  flex: 1;
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 10px;
  position: relative;
}
.assistant .message-content {
  background-color: #ecf5ff;
}
.message-text {
  line-height: 1.5;
  color: #606266;
}
.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  text-align: right;
}
.assistant-suggestions {
  margin-top: 15px;
}
.assistant-suggestions p {
  margin-bottom: 10px;
  color: #909399;
}
.assistant-suggestions .el-button {
  margin-right: 10px;
  margin-bottom: 10px;
}
.hot-topics {
  max-height: 300px;
  overflow-y: auto;
}
.topic-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}
.topic-item:last-child {
  border-bottom: none;
}
.topic-rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-weight: bold;
  color: #606266;
}
.topic-item:nth-child(1) .topic-rank {
  background-color: #f56c6c;
  color: #fff;
}
.topic-item:nth-child(2) .topic-rank {
  background-color: #e6a23c;
  color: #fff;
}
.topic-item:nth-child(3) .topic-rank {
  background-color: #409EFF;
  color: #fff;
}
.topic-content {
  flex: 1;
}
.topic-title {
  margin-bottom: 5px;
  color: #303133;
}
.topic-stats {
  display: flex;
  align-items: center;
  font-size: 12px;
}
.topic-heat {
  color: #e6a23c;
  margin-right: 15px;
}
.topic-sentiment {
  font-weight: bold;
}
.topic-sentiment.positive {
  color: #f56c6c;
}
.topic-sentiment.neutral {
  color: #909399;
}
.topic-sentiment.negative {
  color: #67c23a;
}
.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both
}
</style>
