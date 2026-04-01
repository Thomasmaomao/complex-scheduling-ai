import api from './request'

/**
 * 计算车险报价
 * @param {Object} quoteData - 询价数据
 * @returns {Promise} 报价结果
 */
export function calculateQuote(quoteData) {
  return api.post('/quote/calculate', quoteData)
}

/**
 * 获取测试用例列表
 * @returns {Promise} 测试用例列表
 */
export function getTestCases() {
  return api.get('/quote/test-cases')
}

/**
 * 批量计算报价
 * @param {Array} requests - 询价请求列表
 * @returns {Promise} 批量计算结果
 */
export function batchCalculate(requests) {
  return api.post('/quote/batch-calculate', requests)
}
