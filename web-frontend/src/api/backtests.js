import axios from 'axios';

// 创建一个 apiClient 实例，直接使用完整的后端 URL
const apiClient = axios.create({
  baseURL: 'http://localhost:8003/api', // 直接使用完整的后端 URL
  headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  },
  withCredentials: false, // 允许跨域请求
  timeout: 10000 // 设置超时时间为 10 秒
});

/**
 * 获取指定 ID 的回测报告数据
 * @param {string | number} backtestId - 回测报告的 ID
 * @returns {Promise<object>} - 包含回测报告数据的对象
 * @throws {Error} - 如果 API 请求失败或返回错误状态
 */
export const getBacktestReport = async (backtestId) => {
  if (!backtestId) {
    throw new Error('Backtest ID is required.');
  }

  console.log(`开始获取回测报告，ID: ${backtestId}`);

  // 尝试不同的 API 路径
  const apiPaths = [
    `/strategies/backtest/reports/${backtestId}`,
    `/strategies/backtest/records/${backtestId}`,
    `/backtest/reports/${backtestId}`
  ];

  let lastError = null;

  // 依次尝试每个路径
  for (const path of apiPaths) {
    try {
      console.log(`尝试请求路径: ${path}`);
      const response = await apiClient.get(path);
      console.log(`请求成功: ${path}`, response);

      // 检查响应结构并返回正确的数据
      if (response.data && response.data.data) {
        return response.data.data; // 返回实际的报告数据
      } else if (response.data) {
        return response.data; // 如果没有 .data 字段，返回整个响应数据
      }

      return response; // 如果上面的条件都不满足，返回原始响应
    } catch (error) {
      console.error(`请求路径 ${path} 失败:`, error);
      lastError = error;
      // 继续尝试下一个路径
    }
  }

  // 所有路径都失败了，抛出最后一个错误
  throw lastError || new Error('所有 API 路径请求都失败');
};
