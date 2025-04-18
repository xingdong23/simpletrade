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
