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
