import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()

/**
 * 导航到下一步
 * @param {string} stepName - 步骤名称
 * @param {Array} requiredData - 必需的数据
 */
export const navigateToStep = (stepName, requiredData = []) => {
  if (requiredData.length === 0) {
    router.push(`/admin/${stepName}`)
    ElMessage.success('已保存到下一步')
    return
  }
  
  const hasAllData = requiredData.every(item => item !== null && item !== undefined)
  if (!hasAllData) {
    ElMessage.warning('请先完成当前步骤')
    return
  }
  
  router.push(`/admin/${stepName}`)
  ElMessage.success('已保存到下一步')
}

/**
 * 保存数据到 sessionStorage
 * @param {string} key - 键名
 * @param {any} value - 值
 */
export const saveToSession = (key, value) => {
  try {
    sessionStorage.setItem(key, JSON.stringify(value))
    return true
  } catch (error) {
    console.error('保存失败:', error)
    return false
  }
}

/**
 * 从 sessionStorage 加载数据
 * @param {string} key - 键名
 * @param {any} defaultValue - 默认值
 */
export const loadFromSession = (key, defaultValue = null) => {
  try {
    const data = sessionStorage.getItem(key)
    return data ? JSON.parse(data) : defaultValue
  } catch (error) {
    console.error('加载失败:', error)
    return defaultValue
  }
}

/**
 * 显示错误消息
 * @param {Error} error - 错误对象
 * @param {string} defaultMsg - 默认错误消息
 */
export const showError = (error, defaultMsg = '操作失败') => {
  const errorMsg = error.response?.data?.message || error.message || defaultMsg
  console.error(defaultMsg + ':', error)
  ElMessage.error(defaultMsg + ': ' + errorMsg)
}
