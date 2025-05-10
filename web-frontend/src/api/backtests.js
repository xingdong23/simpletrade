import axios from 'axios';

// 使用与成功请求相同的方式
const API_BASE_URL = 'http://localhost:8003/api';

/**
 * 获取指定 ID 的回测报告数据
 * @param {string | number} backtestId - 回测报告的 ID
 * @returns {Promise<object>} - 包含回测报告数据的对象
 */
export function getBacktestReport(backtestId) {
  if (!backtestId) {
    throw new Error('Backtest ID is required.');
  }

  console.log(`获取回测报告，ID: ${backtestId}`);

  // 使用与成功请求相同的方式
  const url = `${API_BASE_URL}/strategies/backtest/reports/${backtestId}`;
  console.log(`请求URL: ${url}`);

  return axios.get(url);
};
