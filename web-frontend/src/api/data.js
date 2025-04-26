/**
 * 数据管理API
 */

import axios from 'axios'

const API_BASE_URL = 'http://localhost:8003/api'

/**
 * 获取数据概览
 */
export function getDataOverview() {
  return axios.get(`${API_BASE_URL}/data/overview`)
}

/**
 * 获取K线数据
 * @param {string} symbol 代码
 * @param {string} exchange 交易所
 * @param {string} interval 周期
 * @param {string} startDate 开始日期
 * @param {string} endDate 结束日期
 */
export function getBarData(symbol, exchange, interval, startDate, endDate) {
  let url = `${API_BASE_URL}/data/bars?symbol=${symbol}&exchange=${exchange}&interval=${interval}&start_date=${startDate}`

  if (endDate) {
    url += `&end_date=${endDate}`
  }

  return axios.get(url)
}

/**
 * 导入数据
 * @param {object} data 导入数据参数
 */
export function importData(data) {
  return axios.post(`${API_BASE_URL}/data/import`, data)
}

/**
 * 导出数据
 * @param {object} data 导出数据参数
 */
export function exportData(data) {
  return axios.post(`${API_BASE_URL}/data/export`, data)
}

/**
 * 删除数据
 * @param {string} symbol 代码
 * @param {string} exchange 交易所
 * @param {string} interval 周期
 */
export function deleteData(symbol, exchange, interval) {
  return axios.delete(`${API_BASE_URL}/data/bars?symbol=${symbol}&exchange=${exchange}&interval=${interval}`)
}

/**
 * 获取可用的合约代码列表
 * @param {string} exchange 可选，指定交易所筛选
 * @param {string} interval 可选，指定周期筛选
 */
export function getAvailableSymbols(exchange, interval) {
  let url = `${API_BASE_URL}/data/available-symbols`
  const params = {}
  if (exchange) params.exchange = exchange
  if (interval) params.interval = interval
  
  return axios.get(url, { params })
}

/**
 * 获取可用的交易所列表
 * @param {string} symbol 可选，指定合约代码筛选
 * @param {string} interval 可选，指定周期筛选
 */
export function getAvailableExchanges(symbol, interval) {
  let url = `${API_BASE_URL}/data/available-exchanges`
  const params = {}
  if (symbol) params.symbol = symbol
  if (interval) params.interval = interval
  
  return axios.get(url, { params })
}

/**
 * 获取可用的K线周期列表
 * @param {string} symbol 可选，指定合约代码筛选
 * @param {string} exchange 可选，指定交易所筛选
 */
export function getAvailableIntervals(symbol, exchange) {
  let url = `${API_BASE_URL}/data/available-intervals`
  const params = {}
  if (symbol) params.symbol = symbol
  if (exchange) params.exchange = exchange
  
  return axios.get(url, { params })
}

/**
 * 获取所有可用数据记录
 */
export function getAvailableData() {
  return axios.get(`${API_BASE_URL}/data/available-data`)
}
