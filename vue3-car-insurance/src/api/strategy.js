/**
 * 策略管理 API 调用
 * 后端路由：/api/v1/strategy/*
 */
import api from './request'

/**
 * 获取所有策略
 * @param {string} statusFilter - 可选，按状态筛选
 * @param {number} page - 页码，默认 1
 * @param {number} pageSize - 每页数量，默认 20
 */
export function getAllStrategies(statusFilter, page = 1, pageSize = 20) {
  const params = { page, page_size: pageSize }
  if (statusFilter) {
    params.status_filter = statusFilter
  }
  return api.get('/strategy/strategies', { params })
}

/**
 * 获取策略详情
 * @param {string} strategyId - 策略 ID
 */
export function getStrategy(strategyId) {
  return api.get(`/strategy/strategies/${strategyId}`)
}

/**
 * 创建策略
 * @param {Object} data - 策略数据
 */
export function createStrategy(data) {
  return api.post('/strategy/strategies', data)
}

/**
 * 更新策略
 * @param {string} strategyId - 策略 ID
 * @param {Object} data - 更新数据
 */
export function updateStrategy(strategyId, data) {
  return api.put(`/strategy/strategies/${strategyId}`, data)
}

/**
 * 更新策略状态
 * @param {string} strategyId - 策略 ID
 * @param {Object} data - 状态数据
 */
export function updateStrategyStatus(strategyId, data) {
  return api.patch(`/strategy/strategies/${strategyId}/status`, data)
}

/**
 * 记录测试结果
 * @param {string} strategyId - 策略 ID
 * @param {Object} testData - 测试数据
 */
export function recordTestResult(strategyId, testData) {
  return api.post(`/strategy/strategies/${strategyId}/test-results`, testData)
}

/**
 * 发布策略
 * @param {string} strategyId - 策略 ID
 * @param {Object} publishData - 发布数据
 */
export function publishStrategy(strategyId, publishData) {
  return api.post(`/strategy/strategies/${strategyId}/publish`, publishData)
}

/**
 * 获取策略测试历史
 * @param {string} strategyId - 策略 ID
 */
export function getStrategyTestHistory(strategyId) {
  return api.get(`/strategy/strategies/${strategyId}/test-history`)
}

/**
 * 获取策略发布历史
 * @param {string} strategyId - 策略 ID
 */
export function getStrategyPublishHistory(strategyId) {
  return api.get(`/strategy/strategies/${strategyId}/publish-history`)
}

/**
 * 获取策略版本历史（用于历史记录页面）
 * @param {Object} params - 查询参数
 */
export function getStrategyHistory(params = {}) {
  return api.get('/strategy/strategies/history', { params })
}

/**
 * 获取版本详情
 * @param {string} versionId - 版本 ID
 */
export function getVersionDetail(versionId) {
  return api.get(`/strategy/strategies/versions/${versionId}`)
}

/**
 * 回滚到指定版本
 * @param {string} versionId - 版本 ID
 * @param {Object} data - 回滚数据
 */
export function rollbackStrategy(versionId, data = {}) {
  return api.post(`/strategy/strategies/versions/${versionId}/rollback`, data)
}

/**
 * 删除策略
 * @param {string} strategyId - 策略 ID
 */
export function deleteStrategy(strategyId) {
  return api.delete(`/strategy/strategies/${strategyId}`)
}

/**
 * 策略向导 - 步骤 2：保存业务单元
 * @param {string} strategyId - 策略 ID
 * @param {Object} data - 业务单元数据
 */
export function saveWizardBusinessUnit(strategyId, data) {
  return api.put(`/strategy/strategies/${strategyId}/wizard/business-unit`, data)
}

/**
 * 策略向导 - 步骤 3：保存成本模拟
 * @param {string} strategyId - 策略 ID
 * @param {Object} data - 成本模拟数据（包含 global_params 和 business_unit_params）
 */
export function saveWizardCostSimulation(strategyId, data) {
  return api.put(`/strategy/strategies/${strategyId}/wizard/cost-simulation`, data)
}

/**
 * 策略向导 - 步骤 4：保存收益模拟
 * @param {string} strategyId - 策略 ID
 * @param {Object} data - 收益模拟数据
 */
export function saveWizardRevenueSimulation(strategyId, data) {
  return api.put(`/strategy/strategies/${strategyId}/wizard/revenue-simulation`, data)
}

/**
 * 策略向导 - 步骤 5：确认保存
 * @param {string} strategyId - 策略 ID
 */
export function confirmWizard(strategyId) {
  return api.post(`/strategy/strategies/${strategyId}/wizard/confirm`)
}
