/**
 * 策略管理API
 */

import axios from 'axios'

const API_BASE_URL = 'http://localhost:8003/api'

/**
 * 获取策略列表
 * @param {string} type 策略类型，可选值：basic, advanced, component
 * @param {string} category 策略分类，如：趋势跟踪, 震荡指标, 波动性, 选股, AI
 */
export function getStrategies(type, category) {
  let url = `${API_BASE_URL}/strategies/`
  
  // 添加查询参数
  const params = {}
  if (type) params.type = type
  if (category) params.category = category
  
  return axios.get(url, { params })
}

/**
 * 获取策略详情
 * @param {number} strategyId 策略ID
 */
export function getStrategyDetail(strategyId) {
  return axios.get(`${API_BASE_URL}/strategies/${strategyId}`)
}

/**
 * 获取用户策略列表
 * @param {number} userId 用户ID
 */
export function getUserStrategies(userId) {
  return axios.get(`${API_BASE_URL}/strategies/user/${userId}`)
}

/**
 * 获取所有策略类型
 */
export function getStrategyTypes() {
  return axios.get(`${API_BASE_URL}/strategies/types`);
}

/**
 * 获取可用的K线周期列表
 */
export function getAvailableIntervals() {
  return axios.get(`${API_BASE_URL}/strategies/available-intervals`);
}

/**
 * 获取可用的交易所列表
 */
export function getAvailableExchanges() {
  return axios.get(`${API_BASE_URL}/strategies/available-exchanges`);
}

/**
 * 获取可用的合约代码列表
 * @param {object} params 查询参数
 * @param {string} [params.query] 搜索关键词
 * @param {string} [params.exchange] 交易所代码
 */
export function getAvailableSymbols(params) {
  // 注意：这里返回的是原始的axios Promise
  // 前端组件中应该处理 response.data 来获取后端 ApiResponse 格式的数据
  return axios.get(`${API_BASE_URL}/strategies/available-symbols`, { params });
}

/**
 * 运行策略回测
 * @param {object} backtestConfig 回测配置对象
 * @param {number} backtestConfig.strategy_id 
 * @param {string} backtestConfig.symbol
 * @param {string} backtestConfig.exchange
 * @param {string} backtestConfig.interval
 * @param {string} backtestConfig.start_date (YYYY-MM-DD)
 * @param {string} backtestConfig.end_date (YYYY-MM-DD)
 * @param {number} backtestConfig.initial_capital
 * @param {number} backtestConfig.rate
 * @param {number} backtestConfig.slippage
 * @param {object} [backtestConfig.parameters] 可选的用户自定义参数
 * @param {number} backtestConfig.user_id
 */
export function runStrategyBacktest(backtestConfig) {
  return axios.post(`${API_BASE_URL}/strategies/backtest`, backtestConfig);
}

/**
 * 创建用户策略
 * @param {object} userStrategyData 用户策略数据
 * @param {number} userStrategyData.user_id 用户ID
 * @param {number} userStrategyData.strategy_id 策略模板ID
 * @param {string} userStrategyData.name 用户策略名称
 * @param {object} userStrategyData.parameters 策略参数
 * @returns {Promise} 包含创建结果的Promise
 */
export function createUserStrategy(userStrategyData) {
  return axios.post(`${API_BASE_URL}/strategies/user/create`, userStrategyData);
}

/**
 * 获取指定合约、交易所、K线周期的数据可用范围
 * @param {object} params
 * @param {string} params.symbol 合约代码
 * @param {string} params.exchange 交易所代码
 * @param {string} params.interval K线周期
 */
export function getStockDataRange(params) {
  // params should be an object like { symbol: 'AAPL', exchange: 'NASDAQ', interval: '1d' }
  return axios.get(`${API_BASE_URL}/data/stock-data-range`, { params });
}
