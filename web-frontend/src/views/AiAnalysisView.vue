<template>
  <div>
    <!-- 顶部标签导航 -->
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="市场分析" name="market-analysis">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">市场分析</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-select v-model="marketType" placeholder="选择市场" style="width: 150px; margin-right: 10px;">
                <el-option label="美股市场" value="us"></el-option>
                <el-option label="港股市场" value="hk"></el-option>
                <el-option label="中国市场" value="cn"></el-option>
              </el-select>
              <el-button type="primary" icon="el-icon-refresh">刷新分析</el-button>
            </el-col>
          </el-row>
        </div>

        <!-- 市场概况卡片 -->
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="8">
            <el-card shadow="hover">
              <div slot="header" class="clearfix">
                <span>市场情绪</span>
                <el-tag style="float: right;" size="small" type="success">看涨</el-tag>
              </div>
              <div style="text-align: center;">
                <el-progress type="dashboard" :percentage="68" :color="customColors"></el-progress>
                <div style="margin-top: 10px; font-size: 14px;">
                  市场情绪偏向乐观，投资者信心指数连续三周上升。
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover">
              <div slot="header" class="clearfix">
                <span>行业趋势</span>
              </div>
              <div>
                <h4 style="margin: 0 0 15px;">领先行业</h4>
                <el-row style="margin-bottom: 10px;">
                  <el-col :span="8">科技</el-col>
                  <el-col :span="16">
                    <el-progress :percentage="85" color="#409EFF"></el-progress>
                  </el-col>
                </el-row>
                <el-row style="margin-bottom: 10px;">
                  <el-col :span="8">能源</el-col>
                  <el-col :span="16">
                    <el-progress :percentage="72" color="#67C23A"></el-progress>
                  </el-col>
                </el-row>
                <el-row style="margin-bottom: 10px;">
                  <el-col :span="8">金融</el-col>
                  <el-col :span="16">
                    <el-progress :percentage="65" color="#E6A23C"></el-progress>
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover">
              <div slot="header" class="clearfix">
                <span>风险评估</span>
                <el-tag style="float: right;" size="small" type="warning">中等</el-tag>
              </div>
              <div style="text-align: center;">
                <el-progress type="dashboard" :percentage="45" :color="riskColors"></el-progress>
                <div style="margin-top: 10px; font-size: 14px;">
                  市场波动性增大，建议关注利率变化和地缘政治风险。
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 市场热点 -->
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <div slot="header" class="clearfix">
            <span>市场热点</span>
            <el-radio-group v-model="timeFrame" size="small" style="float: right;">
              <el-radio-button label="day">日</el-radio-button>
              <el-radio-button label="week">周</el-radio-button>
              <el-radio-button label="month">月</el-radio-button>
            </el-radio-group>
          </div>
          <el-table :data="hotStocks" style="width: 100%">
            <el-table-column prop="symbol" label="股票代码" width="120"></el-table-column>
            <el-table-column prop="name" label="股票名称" width="180"></el-table-column>
            <el-table-column prop="price" label="当前价格" width="120"></el-table-column>
            <el-table-column prop="change" label="涨跌幅" width="120">
              <template slot-scope="scope">
                <span :style="{ color: scope.row.change >= 0 ? '#67C23A' : '#F56C6C' }">
                  {{ scope.row.change >= 0 ? '+' : '' }}{{ scope.row.change }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="成交量" width="150"></el-table-column>
            <el-table-column prop="sentiment" label="AI情绪分析" width="150">
              <template slot-scope="scope">
                <el-tag :type="scope.row.sentiment === '看涨' ? 'success' : scope.row.sentiment === '看跌' ? 'danger' : 'info'" size="small">
                  {{ scope.row.sentiment }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template slot-scope="scope">
                <el-button size="mini" type="text" @click="viewStockAnalysis(scope.row)">详细分析</el-button>
                <el-button size="mini" type="text" @click="addToWatchlist(scope.row)">添加关注</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="股票预测" name="stock-prediction">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">股票预测</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-autocomplete
                v-model="stockSearch"
                :fetch-suggestions="queryStockSearch"
                placeholder="输入股票代码或名称"
                style="width: 300px; margin-right: 10px;"
              ></el-autocomplete>
              <el-button type="primary" icon="el-icon-search" @click="generatePrediction">生成预测</el-button>
            </el-col>
          </el-row>
        </div>
        
        <el-card v-if="!selectedStock" shadow="hover" style="margin-bottom: 20px; text-align: center; padding: 60px 0;">
          <i class="el-icon-search" style="font-size: 48px; color: #909399; margin-bottom: 20px;"></i>
          <p style="font-size: 16px; color: #606266;">请输入股票代码或名称进行预测分析</p>
        </el-card>
        
        <div v-else>
          <!-- 股票基本信息 -->
          <el-card shadow="hover" style="margin-bottom: 20px;">
            <el-row :gutter="20">
              <el-col :span="6">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">当前价格</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #303133; margin: 0;">{{ selectedStock.price }}</p>
                  <div style="margin-top: 10px; font-size: 14px;" :style="{ color: selectedStock.change >= 0 ? '#67C23A' : '#F56C6C' }">
                    <i :class="selectedStock.change >= 0 ? 'el-icon-top' : 'el-icon-bottom'"></i>
                    {{ selectedStock.change >= 0 ? '+' : '' }}{{ selectedStock.change }}% 今日
                  </div>
                </div>
              </el-col>
              
              <el-col :span="6">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">预测价格 (7日)</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #303133; margin: 0;">{{ selectedStock.prediction7d }}</p>
                  <div style="margin-top: 10px; font-size: 14px;" :style="{ color: selectedStock.prediction7dChange >= 0 ? '#67C23A' : '#F56C6C' }">
                    <i :class="selectedStock.prediction7dChange >= 0 ? 'el-icon-top' : 'el-icon-bottom'"></i>
                    {{ selectedStock.prediction7dChange >= 0 ? '+' : '' }}{{ selectedStock.prediction7dChange }}%
                  </div>
                </div>
              </el-col>
              
              <el-col :span="6">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">预测价格 (30日)</h3>
                  <p style="font-size: 24px; font-weight: 600; color: #303133; margin: 0;">{{ selectedStock.prediction30d }}</p>
                  <div style="margin-top: 10px; font-size: 14px;" :style="{ color: selectedStock.prediction30dChange >= 0 ? '#67C23A' : '#F56C6C' }">
                    <i :class="selectedStock.prediction30dChange >= 0 ? 'el-icon-top' : 'el-icon-bottom'"></i>
                    {{ selectedStock.prediction30dChange >= 0 ? '+' : '' }}{{ selectedStock.prediction30dChange }}%
                  </div>
                </div>
              </el-col>
              
              <el-col :span="6">
                <div style="text-align: center;">
                  <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">AI建议</h3>
                  <p style="font-size: 24px; font-weight: 600; margin: 0;">
                    <el-tag :type="selectedStock.recommendation === '买入' ? 'success' : selectedStock.recommendation === '卖出' ? 'danger' : 'warning'" size="medium">
                      {{ selectedStock.recommendation }}
                    </el-tag>
                  </p>
                  <div style="margin-top: 10px; font-size: 14px; color: #909399;">
                    置信度: {{ selectedStock.confidence }}%
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>
          
          <!-- 预测图表 -->
          <el-card shadow="hover" style="margin-bottom: 20px;">
            <div slot="header" class="clearfix">
              <span>价格预测图表</span>
              <el-radio-group v-model="predictionTimeframe" size="small" style="float: right;">
                <el-radio-button label="7d">7天</el-radio-button>
                <el-radio-button label="30d">30天</el-radio-button>
                <el-radio-button label="90d">90天</el-radio-button>
              </el-radio-group>
            </div>
            <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: #909399;">
              <i class="el-icon-data-line" style="font-size: 24px; margin-right: 10px;"></i>
              价格预测图表（这里将显示图表）
            </div>
          </el-card>
          
          <!-- 分析报告 -->
          <el-card shadow="hover">
            <div slot="header" class="clearfix">
              <span>AI分析报告</span>
            </div>
            <div>
              <h4>技术分析</h4>
              <p>{{ selectedStock.technicalAnalysis }}</p>
              
              <el-divider></el-divider>
              
              <h4>基本面分析</h4>
              <p>{{ selectedStock.fundamentalAnalysis }}</p>
              
              <el-divider></el-divider>
              
              <h4>风险因素</h4>
              <p>{{ selectedStock.riskFactors }}</p>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="模型训练" name="model-training">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">模型训练</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="primary" icon="el-icon-plus" @click="createNewModel">新建模型</el-button>
            </el-col>
          </el-row>
        </div>
        
        <!-- 模型列表 -->
        <el-table :data="models" style="width: 100%" border>
          <el-table-column prop="name" label="模型名称" width="180"></el-table-column>
          <el-table-column prop="type" label="模型类型" width="150">
            <template slot-scope="scope">
              <el-tag :type="scope.row.type === 'LSTM' ? 'primary' : scope.row.type === 'CNN' ? 'success' : 'warning'" size="small">
                {{ scope.row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="target" label="预测目标" width="150"></el-table-column>
          <el-table-column prop="accuracy" label="准确率" width="120">
            <template slot-scope="scope">
              <el-progress :percentage="scope.row.accuracy" :format="percentFormat"></el-progress>
            </template>
          </el-table-column>
          <el-table-column prop="lastTrained" label="上次训练时间" width="180"></el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template slot-scope="scope">
              <el-tag :type="scope.row.status === '已部署' ? 'success' : scope.row.status === '训练中' ? 'warning' : 'info'" size="small">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template slot-scope="scope">
              <el-button size="mini" type="text" @click="viewModelDetails(scope.row)">查看</el-button>
              <el-button size="mini" type="text" @click="trainModel(scope.row)" :disabled="scope.row.status === '训练中'">训练</el-button>
              <el-button 
                size="mini" 
                type="text" 
                @click="deployModel(scope.row)" 
                :disabled="scope.row.status === '训练中' || scope.row.status === '已部署'"
              >
                部署
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 新建模型对话框 -->
    <el-dialog title="新建AI模型" :visible.sync="modelDialogVisible" width="50%">
      <el-form :model="newModelForm" label-width="120px">
        <el-form-item label="模型名称">
          <el-input v-model="newModelForm.name" placeholder="请输入模型名称"></el-input>
        </el-form-item>
        <el-form-item label="模型类型">
          <el-select v-model="newModelForm.type" placeholder="请选择模型类型" style="width: 100%;">
            <el-option label="LSTM (长短期记忆网络)" value="LSTM"></el-option>
            <el-option label="CNN (卷积神经网络)" value="CNN"></el-option>
            <el-option label="GRU (门控循环单元)" value="GRU"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="预测目标">
          <el-select v-model="newModelForm.target" placeholder="请选择预测目标" style="width: 100%;">
            <el-option label="价格预测" value="price"></el-option>
            <el-option label="趋势预测" value="trend"></el-option>
            <el-option label="波动率预测" value="volatility"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="训练数据">
          <el-select v-model="newModelForm.dataSource" placeholder="请选择数据源" style="width: 100%;">
            <el-option label="美股市场数据" value="us"></el-option>
            <el-option label="港股市场数据" value="hk"></el-option>
            <el-option label="中国市场数据" value="cn"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="训练周期">
          <el-slider v-model="newModelForm.epochs" :min="10" :max="100" :step="10" show-stops></el-slider>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="modelDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitNewModel">创建</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AIAnalysisView',
  data() {
    return {
      activeTab: 'market-analysis',
      marketType: 'us',
      timeFrame: 'week',
      stockSearch: '',
      selectedStock: null,
      predictionTimeframe: '30d',
      modelDialogVisible: false,
      customColors: [
        {color: '#F56C6C', percentage: 20},
        {color: '#E6A23C', percentage: 40},
        {color: '#5CB87A', percentage: 60},
        {color: '#1989FA', percentage: 80},
        {color: '#6F7AD3', percentage: 100}
      ],
      riskColors: [
        {color: '#6F7AD3', percentage: 20},
        {color: '#1989FA', percentage: 40},
        {color: '#E6A23C', percentage: 60},
        {color: '#F56C6C', percentage: 80},
        {color: '#FF0000', percentage: 100}
      ],
      hotStocks: [
        {
          symbol: 'AAPL',
          name: 'Apple Inc.',
          price: '182.50',
          change: 2.3,
          volume: '45.2M',
          sentiment: '看涨'
        },
        {
          symbol: 'TSLA',
          name: 'Tesla, Inc.',
          price: '245.30',
          change: -1.5,
          volume: '32.8M',
          sentiment: '中性'
        },
        {
          symbol: 'NVDA',
          name: 'NVIDIA Corporation',
          price: '485.20',
          change: 3.8,
          volume: '28.5M',
          sentiment: '看涨'
        },
        {
          symbol: 'MSFT',
          name: 'Microsoft Corporation',
          price: '340.25',
          change: 1.2,
          volume: '22.1M',
          sentiment: '看涨'
        },
        {
          symbol: 'AMZN',
          name: 'Amazon.com, Inc.',
          price: '178.75',
          change: -0.8,
          volume: '18.9M',
          sentiment: '中性'
        }
      ],
      models: [
        {
          name: 'LSTM股价预测模型',
          type: 'LSTM',
          target: '价格预测',
          accuracy: 78,
          lastTrained: '2023-10-10 15:30:45',
          status: '已部署'
        },
        {
          name: 'CNN趋势识别模型',
          type: 'CNN',
          target: '趋势预测',
          accuracy: 82,
          lastTrained: '2023-10-12 09:15:20',
          status: '已训练'
        },
        {
          name: 'GRU波动率预测',
          type: 'GRU',
          target: '波动率预测',
          accuracy: 65,
          lastTrained: '2023-10-08 11:45:30',
          status: '训练中'
        }
      ],
      newModelForm: {
        name: '',
        type: '',
        target: '',
        dataSource: '',
        epochs: 50
      }
    }
  },
  methods: {
    percentFormat(percentage) {
      return `${percentage}%`;
    },
    queryStockSearch(queryString, callback) {
      const results = [
        { value: 'AAPL - Apple Inc.' },
        { value: 'MSFT - Microsoft Corporation' },
        { value: 'GOOGL - Alphabet Inc.' },
        { value: 'AMZN - Amazon.com, Inc.' },
        { value: 'TSLA - Tesla, Inc.' }
      ];
      callback(queryString ? results.filter(item => item.value.toLowerCase().includes(queryString.toLowerCase())) : results);
    },
    generatePrediction() {
      // 模拟生成预测结果
      if (this.stockSearch.includes('AAPL')) {
        this.selectedStock = {
          symbol: 'AAPL',
          name: 'Apple Inc.',
          price: '$182.50',
          change: 2.3,
          prediction7d: '$187.25',
          prediction7dChange: 2.6,
          prediction30d: '$195.80',
          prediction30dChange: 7.3,
          recommendation: '买入',
          confidence: 85,
          technicalAnalysis: 'AAPL股票目前处于上升趋势，突破了200日均线，MACD指标显示强劲的买入信号。相对强弱指标(RSI)为65，表明股票有上升动能但尚未达到超买区域。',
          fundamentalAnalysis: 'Apple公司最近财报显示营收和利润均超出市场预期，iPhone销售强劲，服务业务持续增长。公司现金储备充足，有能力继续进行股票回购和派发股息。',
          riskFactors: '全球供应链问题可能影响产品生产和交付。科技行业竞争激烈，创新压力大。监管风险增加，特别是在应用商店和隐私政策方面。'
        };
      } else if (this.stockSearch) {
        this.$message({
          message: '暂无该股票的预测数据，请尝试搜索"AAPL"',
          type: 'warning'
        });
      }
    },
    viewStockAnalysis(stock) {
      this.activeTab = 'stock-prediction';
      this.stockSearch = `${stock.symbol} - ${stock.name}`;
      this.generatePrediction();
    },
    addToWatchlist(stock) {
      this.$message({
        message: `已将 ${stock.name} 添加到关注列表`,
        type: 'success'
      });
    },
    createNewModel() {
      this.modelDialogVisible = true;
    },
    submitNewModel() {
      this.$message({
        message: '新模型创建成功，已加入训练队列',
        type: 'success'
      });
      this.modelDialogVisible = false;
    },
    viewModelDetails(model) {
      this.$message({
        message: `查看模型详情: ${model.name}`,
        type: 'info'
      });
    },
    trainModel(model) {
      this.$message({
        message: `开始训练模型: ${model.name}`,
        type: 'success'
      });
    },
    deployModel(model) {
      this.$message({
        message: `模型 ${model.name} 已成功部署`,
        type: 'success'
      });
    }
  }
}
</script>

<style>
.el-tabs__header {
  margin-bottom: 25px;
}
</style>
