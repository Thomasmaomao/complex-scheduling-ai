/**
 * 策略数据转换工具函数
 * 用于将后端 API 返回的策略数据转换为前端 UI 格式
 */

import { getAllStrategies } from '../api/strategy'

/**
 * 加载策略列表并转换为前端格式
 * @param {Object} options - 配置选项
 * @param {String} options.statusFilter - 状态过滤（可选）
 * @param {Function} options.onError - 错误处理回调（可选）
 * @returns {Promise<Array>} 转换后的策略列表
 */
export async function loadStrategiesForUI(options = {}) {
  const { statusFilter, onError } = options
  
  try {
    // getAllStrategies 返回 response.data，包含 {total, page, page_size, strategies}
    const response = await getAllStrategies(statusFilter)
    
    // 提取 strategies 数组
    const strategies = response.strategies || response.data?.strategies || []
    
    // 数据格式转换：后端字段 → 前端 UI 格式
    return strategies.map(strategy => ({
      id: strategy.id,
      name: strategy.name,
      description: strategy.description,
      status: strategy.status,
      institutions: strategy.institutions || [],
      // 兼容后端字段命名（business_units 或 businessUnits）
      businessUnits: strategy.business_units || strategy.businessUnits || [],
      // 数据格式转换：后端比率 (0-1) → 前端权重 (0-100)
      priority_weights: {
        price: Math.round(strategy.fixed_cost_ratio * 100),
        service: Math.round(strategy.target_loss_ratio * 100),
        claim: Math.round(strategy.market_expense_ratio * 100)
      }
    }))
  } catch (error) {
    console.error('加载策略失败:', error)
    if (onError) {
      onError(error)
    }
    throw error
  }
}

/**
 * 将前端策略数据转换为后端 API 格式
 * @param {Object} strategy - 前端策略对象
 * @returns {Object} 后端 API 格式的策略数据
 */
export function transformStrategyToBackend(strategy) {
  // 问题 10：添加输入参数验证
  if (!strategy || !strategy.priority_weights) {
    throw new Error('Invalid strategy data: missing required fields');
  }
  
  if (!strategy.priority_weights.price || !strategy.priority_weights.service || !strategy.priority_weights.claim) {
    throw new Error('Invalid strategy data: missing priority_weights fields');
  }
  
  return {
    name: strategy.strategy_name || strategy.name,
    description: strategy.description,
    // 数据格式转换：前端权重 (0-100) → 后端比率 (0-1)
    fixed_cost_ratio: strategy.priority_weights.price / 100,
    target_loss_ratio: strategy.priority_weights.service / 100,
    market_expense_ratio: strategy.priority_weights.claim / 100,
    autonomous_discount_min: strategy.autonomous_discount_min || 0.50,
    autonomous_discount_max: strategy.autonomous_discount_max || 0.65,
    institutions: strategy.institutions?.map(name => ({
      code: name.toLowerCase(),
      name
    })) || [],
    // 问题 5：统一返回驼峰命名 businessUnits
    businessUnits: strategy.businessUnits || strategy.business_units || [],
    business_units: strategy.business_units || strategy.businessUnits || []
  }
}
