<template>
  <div class="business-unit-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1>步骤 1：业务单元划分</h1>
        <p class="description">选择参与策略配置的业务单元</p>
      </div>
    </div>

    <!-- 步骤进度条 -->
    <div class="steps-container">
      <div class="step-item active">
        <div class="step-icon">1</div>
        <div class="step-label">业务单元划分</div>
      </div>
      <div class="step-line"></div>
      <div class="step-item">
        <div class="step-icon">2</div>
        <div class="step-label">成本模拟</div>
      </div>
      <div class="step-line"></div>
      <div class="step-item">
        <div class="step-icon">3</div>
        <div class="step-label">收益模拟</div>
      </div>
      <div class="step-line"></div>
      <div class="step-item">
        <div class="step-icon">4</div>
        <div class="step-label">确认保存</div>
      </div>
    </div>

    <!-- 业务单元列表 -->
    <div class="table-section">
      <div class="section-header">
        <div class="header-left">
          <div class="section-indicator"></div>
          <h3>业务单元列表</h3>
        </div>
        <div class="header-actions">
          <el-button size="small" @click="handleSelectAll">
            {{ allSelected ? '取消全选' : '全选' }}
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 50px;" class="text-center">选择</th>
              <th>业务单元 ID</th>
              <th>业务单元名称</th>
              <th>说明</th>
              <th class="text-right">保单数</th>
              <th class="text-right">平均保费</th>
              <th class="text-right">保费规模</th>
              <th class="text-center">预期利润率</th>
              <th class="text-center">策略建议</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="unit in businessUnits" 
              :key="unit.unit_id"
              :class="['table-row', isSelected(unit) ? 'selected' : '']"
            >
              <td class="text-center">
                <input 
                  type="checkbox" 
                  :checked="isSelected(unit)"
                  @change="toggleSelection(unit)"
                  class="row-checkbox"
                />
              </td>
              <td class="unit-id">{{ unit.unit_id }}</td>
              <td class="unit-name">{{ unit.unit_name }}</td>
              <td class="unit-desc">{{ unit.description || '-' }}</td>
              <td class="text-right number">{{ unit.policy_count?.toLocaleString() }}</td>
              <td class="text-right number">¥{{ unit.avg_premium?.toLocaleString() || '-' }}</td>
              <td class="text-right number">¥{{ (unit.premium_scale / 10000).toFixed(0) }}万</td>
              <td class="text-center">
                <span class="margin-badge" :class="getMarginClass(unit.expected_profit_margin)">
                  {{ (unit.expected_profit_margin * 100).toFixed(1) }}%
                </span>
              </td>
              <td class="text-center">
                <span class="suggestion-badge" :class="getSuggestionClass(unit.strategy_suggestion)">
                  {{ unit.strategy_suggestion }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 汇总数据 -->
    <div class="summary-section" v-if="selectedUnits.length > 0">
      <div class="summary-header">
        <h4>已选择 {{ selectedUnits.length }} 个业务单元</h4>
      </div>
      <div class="summary-grid">
        <div class="summary-item">
          <div class="summary-item-label">总保单数</div>
          <div class="summary-item-value">
            {{ totalPolicyCount.toLocaleString() }}
            <span class="summary-unit">单</span>
          </div>
        </div>
        <div class="summary-item">
          <div class="summary-item-label">总保费规模</div>
          <div class="summary-item-value">
            ¥{{ (totalPremium / 10000).toFixed(0) }}
            <span class="summary-unit">万元</span>
          </div>
        </div>
        <div class="summary-item">
          <div class="summary-item-label">平均利润率</div>
          <div class="summary-item-value" :class="getMarginClass(avgProfitMargin)">
            {{ (avgProfitMargin * 100).toFixed(1) }}%
          </div>
        </div>
        <div class="summary-item">
          <div class="summary-item-label">风险等级</div>
          <div class="summary-item-value">
            <span class="risk-badge" :class="getRiskClass(overallRiskLevel)">
              {{ overallRiskLevel }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <div class="footer-actions">
      <el-button @click="handleReset">重置</el-button>
      <div class="footer-right">
        <el-button type="primary" @click="handleNext" :loading="loading">
          下一步：成本模拟
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)

// 业务单元数据
const businessUnits = ref([
  {
    unit_id: 'BU001',
    unit_name: '燃油车 - 续保',
    description: '传统燃油车续保客户群体',
    vehicle_type: '燃油车',
    policy_count: 5000,
    avg_premium: 3500,
    premium_scale: 17500000,
    expected_profit_margin: 0.08,
    strategy_suggestion: '重点发展'
  },
  {
    unit_id: 'BU002',
    unit_name: '燃油车 - 新保',
    description: '传统燃油车新保客户群体',
    vehicle_type: '燃油车',
    policy_count: 2000,
    avg_premium: 4800,
    premium_scale: 9600000,
    expected_profit_margin: 0.03,
    strategy_suggestion: '稳定发展'
  },
  {
    unit_id: 'BU003',
    unit_name: '新能源 - 高价值',
    description: '高价值新能源汽车客户',
    vehicle_type: '新能源',
    policy_count: 1500,
    avg_premium: 5800,
    premium_scale: 8700000,
    expected_profit_margin: 0.05,
    strategy_suggestion: '谨慎发展'
  },
  {
    unit_id: 'BU004',
    unit_name: '新能源 - 普通',
    description: '普通新能源汽车客户',
    vehicle_type: '新能源',
    policy_count: 3000,
    avg_premium: 4500,
    premium_scale: 13500000,
    expected_profit_margin: -0.03,
    strategy_suggestion: '限制发展'
  },
  {
    unit_id: 'BU005',
    unit_name: '豪车 - 续保',
    description: '豪华车续保客户群体',
    vehicle_type: '燃油车',
    policy_count: 500,
    avg_premium: 15000,
    premium_scale: 7500000,
    expected_profit_margin: 0.12,
    strategy_suggestion: '优质业务'
  }
])

// 选中的业务单元 - 默认全选所有业务单元
const selectedUnits = ref([...businessUnits.value])
const allSelected = ref(true)

// 计算属性
const totalPolicyCount = computed(() => {
  return selectedUnits.value.reduce((sum, unit) => sum + unit.policy_count, 0)
})

const totalPremium = computed(() => {
  return selectedUnits.value.reduce((sum, unit) => sum + unit.premium_scale, 0)
})

const avgProfitMargin = computed(() => {
  if (selectedUnits.value.length === 0) return 0
  const total = selectedUnits.value.reduce((sum, unit) => sum + unit.expected_profit_margin, 0)
  return total / selectedUnits.value.length
})

const overallRiskLevel = computed(() => {
  if (selectedUnits.value.length === 0) return '未选择'
  
  const hasHighRisk = selectedUnits.value.some(u => u.strategy_suggestion === '限制发展')
  const hasLowRisk = selectedUnits.value.every(u => 
    ['重点发展', '优质业务'].includes(u.strategy_suggestion)
  )
  
  if (hasHighRisk) return '高风险'
  if (hasLowRisk) return '低风险'
  return '中风险'
})

// 方法
const isSelected = (unit) => {
  return selectedUnits.value.some(u => u.unit_id === unit.unit_id)
}

const toggleSelection = (unit) => {
  const index = selectedUnits.value.findIndex(u => u.unit_id === unit.unit_id)
  if (index === -1) {
    selectedUnits.value.push(unit)
  } else {
    selectedUnits.value.splice(index, 1)
  }
  allSelected.value = selectedUnits.value.length === businessUnits.value.length
}

const handleSelectionChange = (selection) => {
  selectedUnits.value = selection
  allSelected.value = selection.length === businessUnits.value.length
}

const handleSelectAll = () => {
  if (allSelected.value) {
    selectedUnits.value = []
    allSelected.value = false
  } else {
    selectedUnits.value = [...businessUnits.value]
    allSelected.value = true
  }
}

const handleReset = () => {
  selectedUnits.value = []
  allSelected.value = false
  ElMessage.info('已重置选择')
}

const handleNext = async () => {
  if (selectedUnits.value.length === 0) {
    ElMessage.warning('请至少选择一个业务单元')
    return
  }
  
  loading.value = true
  try {
    sessionStorage.setItem('selectedBusinessUnits', JSON.stringify(selectedUnits.value.map(u => u.unit_id)))
    ElMessage.success('选择已保存，跳转到成本模拟')
    router.push('/admin/cost-simulation')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 工具函数
const getMarginClass = (margin) => {
  if (margin >= 0.08) return 'high'
  if (margin >= 0.05) return 'medium'
  if (margin >= 0.03) return 'low'
  return 'negative'
}

const getSuggestionClass = (suggestion) => {
  return suggestion.replace(/\s+/g, '-')
}

const getRiskClass = (risk) => {
  if (risk === '低风险') return 'low'
  if (risk === '中风险') return 'medium'
  if (risk === '高风险') return 'high'
  return 'default'
}
</script>

<style scoped>
.business-unit-page {
  padding: 24px;
  min-height: 100vh;
  background: #f5f7fa;
}

/* 页面头部 */
.page-header {
  margin-bottom: 20px;
}

.header-content h1 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.description {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

/* 步骤进度条 */
.steps-container {
  display: flex;
  align-items: center;
  background: white;
  padding: 20px 24px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 0 0 auto;
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e4e7ed;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
}

.step-item.active .step-icon {
  background: linear-gradient(135deg, #002d81 0%, #712ae2 100%);
  color: white;
}

.step-label {
  font-size: 12px;
  color: #909399;
}

.step-item.active .step-label {
  color: #002d81;
  font-weight: 600;
}

.step-line {
  flex: 1;
  height: 2px;
  background: #e4e7ed;
  margin: 0 16px;
}

/* 表格区域 */
.table-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-indicator {
  width: 6px;
  height: 24px;
  background: #002d81;
  border-radius: 3px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead {
  background: #f5f7fa;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
  white-space: nowrap;
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #ebeef5;
}

.table-row:hover {
  background: #f5f7fa;
}

.table-row.selected {
  background: #ecf5ff;
}

.row-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.unit-id {
  font-family: 'Segoe UI', Arial, sans-serif;
  font-weight: 600;
  color: #909399;
  font-size: 12px;
}

.unit-name {
  font-weight: 600;
  color: #303133;
}

.unit-desc {
  color: #909399;
  font-size: 12px;
}

.number {
  font-family: 'Segoe UI', Arial, sans-serif;
  font-weight: 600;
  color: #303133;
}

.margin-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.margin-badge.high {
  background: #f0f9eb;
  color: #67c23a;
}

.margin-badge.medium {
  background: #ecf5ff;
  color: #409eff;
}

.margin-badge.low {
  background: #fdf6ec;
  color: #e6a23c;
}

.margin-badge.negative {
  background: #fef0f0;
  color: #f56c6c;
}

.suggestion-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.suggestion-badge.focus-development {
  background: #f0f9eb;
  color: #67c23a;
}

.suggestion-badge.stable-development {
  background: #ecf5ff;
  color: #409eff;
}

.suggestion-badge.cautious-development {
  background: #fdf6ec;
  color: #e6a23c;
}

.suggestion-badge.restricted-development {
  background: #fef0f0;
  color: #f56c6c;
}

.suggestion-badge.quality-business {
  background: #f0f9eb;
  color: #67c23a;
}

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
}

/* 汇总区域 */
.summary-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.summary-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.summary-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.summary-item {
  background: white;
  padding: 20px;
  text-align: center;
}

.summary-item-label {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 10px;
}

.summary-item-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  font-family: 'Segoe UI', Arial, sans-serif;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.summary-item-value.high {
  color: #67c23a;
}

.summary-item-value.medium {
  color: #409eff;
}

.summary-item-value.low {
  color: #e6a23c;
}

.summary-item-value.negative {
  color: #f56c6c;
}

.summary-unit {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}

.risk-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
}

.risk-badge.low {
  background: #f0f9eb;
  color: #67c23a;
}

.risk-badge.medium {
  background: #fdf6ec;
  color: #e6a23c;
}

.risk-badge.high {
  background: #fef0f0;
  color: #f56c6c;
}

.risk-badge.default {
  background: #f5f7fa;
  color: #909399;
}

/* 底部操作 */
.footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.footer-right {
  display: flex;
  gap: 12px;
}
</style>
