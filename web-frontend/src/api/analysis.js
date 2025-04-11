/**
 * 数据分析API
 */

import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

/**
 * 计算技术指标
 * @param {object} data 计算参数
 */
export function calculateIndicators(data) {
  return axios.post(`${API_BASE_URL}/analysis/indicators`, data)
}

/**
 * 运行策略回测
 * @param {object} data 回测参数
 */
export function runBacktest(data) {
  return axios.post(`${API_BASE_URL}/analysis/backtest`, data)
}
