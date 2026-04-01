<template>
  <div class="revenue-simulation-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1>步骤 3：收益模拟</h1>
        <p class="description">多情景模拟各业务单元收益，评估策略可行性</p>
      </div>
    </div>

    <!-- 步骤进度条 -->
    <div class="steps-container">
      <div class="step-item">
        <div class="step-icon">1</div>
        <div class="step-label">业务单元</div>
      </div>
      <div class="step-line"></div>
      <div class="step-item">
        <div class="step-icon">2</div>
        <div class="step-label">成本模拟</div>
      </div>
      <div class="step-line"></div>
      <div class="step-item active">
        <div class="step-icon">3</div>
        <div class="step-label">收益模拟</div>
      </div>
      <div class="step-line"></div>
      <div class="step-item">
        <div class="step-icon">4</div>
        <div class="step-label">确认保存</div>
      </div>
    </div>

    <!-- 各业务单元预期收益 -->
    <div class="table-section">
      <div class="section-header">
        <div class="header-left">
          <div class="section-indicator"></div>
          <h3>各业务单元预期收益</h3>
        </div>
        <div class="header-actions">
          <el-button type="primary" size="small" @click="calculateAll">
            <span class="icon">🔢</span> 整体测算
          </el-button>
          <el-button type="success" size="small" @click="exportReport">
            <span class="icon">📥</span> 导出模拟明细表
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 40px;"></th>
              <th>业务单元</th>
              <th class="text-right">保单数</th>
              <th class="text-right">平均保费</th>
              <th class="text-right">保费规模</th>
              <th class="text-right">纯风险成本</th>
              <th class="text-right">预期利润率</th>
              <th class="text-center">多情景模拟</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(unit, index) in businessUnits" :key="unit.unit_id">
              <!-- 主行 -->
              <tr class="table-row">
                <td class="text-center">
                  <button 
                    class="expand-btn" 
                    @click="toggleExpand(index)"
                    :class="{ expanded: expandedRows.includes(index) }"
                  >
                    {{ expandedRows.includes(index) ? '▲' : '▼' }}
                  </button>
                </td>
                <td class="unit-name-cell">{{ unit.unit_name }}</td>
                <td class="text-right number">{{ unit.policy_count?.toLocaleString() }}</td>
                <td class="text-right number">¥{{ (unit.avg_premium || 3500)?.toLocaleString() }}</td>
                <td class="text-right number">¥{{ ((unit.policy_count || 0) * (unit.avg_premium || 3500) / 10000).toFixed(0) }}万</td>
                <td class="text-right number">¥{{ (unit.rp || 0).toFixed(0) }}</td>
                <td class="text-center">
                  <span class="margin-badge" :class="getMarginClass(unit.profit_margin)">
                    {{ (unit.profit_margin * 100).toFixed(1) }}%
                  </span>
                </td>
                <td class="text-center">
                  <button class="scenario-btn" @click="toggleExpand(index)">
                    展开
                  </button>
                </td>
              </tr>
              
              <!-- 展开的情景测试行 -->
              <tr v-if="expandedRows.includes(index)" class="expand-row">
                <td colspan="7" class="expand-content">
                  <div class="scenario-panel">
                    <!-- 情景标签页 -->
                    <div class="scenario-tabs">
                      <div 
                        v-for="scenario in scenarios" 
                        :key="scenario.id"
                        :class="['scenario-tab', unit.selectedScenario === scenario.id ? 'active' : '']"
                        @click="selectScenario(unit, scenario.id)"
                      >
                        {{ scenario.name }}
                      </div>
                    </div>
                    
                    <!-- 情景汇总 -->
                    <div class="scenario-summary-grid">
                      <div class="summary-box">
                        <div class="summary-box-label">预期保单</div>
                        <div class="summary-box-value">{{ calculateScenarioPolicyCount(unit, unit.selectedScenario).toLocaleString() }}单</div>
                      </div>
                      <div class="summary-box">
                        <div class="summary-box-label">预期保费</div>
                        <div class="summary-box-value">¥{{ (calculateScenarioPremium(unit, unit.selectedScenario) / 10000).toFixed(0) }}万</div>
                      </div>
                      <div class="summary-box">
                        <div class="summary-box-label">预期利润</div>
                        <div class="summary-box-value" :class="calculateScenarioProfit(unit, unit.selectedScenario) >= 0 ? 'positive' : 'negative'">
                          {{ (calculateScenarioProfit(unit, unit.selectedScenario) / 10000).toFixed(0) }}万
                        </div>
                      </div>
                      <div class="summary-box">
                        <div class="summary-box-label">利润率</div>
                        <div class="summary-box-value" :class="getMarginClass(calculateScenarioMargin(unit, unit.selectedScenario))">
                          {{ (calculateScenarioMargin(unit, unit.selectedScenario) * 100).toFixed(1) }}%
                        </div>
                      </div>
                    </div>
                    
                    <!-- 五情景对比表格 -->
                    <div class="scenario-comparison-table">
                      <div class="comparison-grid">
                        <div 
                          v-for="scenario in scenarios" 
                          :key="scenario.id"
                          :class="['comparison-item', unit.selectedScenario === scenario.id ? 'selected' : '']"
                        >
                          <div class="comparison-header">{{ scenario.name }}</div>
                          <div class="comparison-data">
                            <div class="data-row">
                              <span class="data-label">利润额</span>
                              <span class="data-value" :class="scenario.id === 'base' ? 'highlight' : ''">
                                {{ (calculateScenarioProfit(unit, scenario.id) / 10000).toFixed(0) }}万
                              </span>
                            </div>
                            <div class="data-row">
                              <span class="data-label">利润率</span>
                              <span class="data-value-small" :class="scenario.id === 'base' ? 'highlight' : ''">
                                {{ (calculateScenarioMargin(unit, scenario.id) * 100).toFixed(1) }}%
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- 应用按钮 -->
                    <div class="scenario-actions">
                      <el-button type="primary" size="small" @click="applyScenario(unit)">应用此情景</el-button>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 整体业务汇总 -->
    <div class="summary-section">
      <div class="section-header">
        <div class="header-left">
          <div class="section-indicator primary"></div>
          <h3>整体业务汇总</h3>
        </div>
      </div>

      <div class="summary-grid">
        <div class="summary-item">
          <div class="summary-item-label">总保单数</div>
          <div class="summary-item-value">
            {{ totalPolicyCount.toLocaleString() }}
            <span class="summary-unit">件</span>
          </div>
        </div>
        <div class="summary-item">
          <div class="summary-item-label">总保费</div>
          <div class="summary-item-value">
            {{ (totalPremium / 10000).toFixed(0) }}
            <span class="summary-unit">万</span>
          </div>
        </div>
        <div class="summary-item">
          <div class="summary-item-label">总利润</div>
          <div class="summary-item-value" :class="totalExpectedProfit >= 0 ? 'positive' : 'negative'">
            {{ (totalExpectedProfit / 10000).toFixed(0) }}
            <span class="summary-unit">万</span>
            <el-tag 
              :type="totalExpectedProfit >= 0 ? 'success' : 'danger'" 
              size="small" 
              effect="light"
              class="status-tag"
            >
              <span class="icon">📈</span> 良好
            </el-tag>
          </div>
        </div>
        <div class="summary-item">
          <div class="summary-item-label">整体利润率</div>
          <div class="summary-item-value">
            {{ (avgProfitMargin * 100).toFixed(1) }}
            <span class="summary-percent">%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <div class="footer-actions">
      <el-button @click="handleBack">上一步</el-button>
      <div class="footer-right">
        <el-button @click="handleTempSave">暂时保存</el-button>
        <el-button type="success" @click="handleSave">保存策略</el-button>
      </div>
    </div>

    <!-- 保存策略弹窗 -->
    <el-dialog v-model="saveDialogVisible" title="保存策略" width="500px">
      <el-form :model="strategyForm" label-width="100px">
        <el-form-item label="策略名称" required>
          <el-input v-model="strategyForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略描述">
          <el-input 
            v-model="strategyForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入策略描述" 
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="success" @click="confirmSave">保存策略</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const saveDialogVisible = ref(false)
const expandedRows = ref([])

// 策略表单
const strategyForm = reactive({
  name: '',
  description: ''
})

// 情景定义
const scenarios = [
  { id: 's1', name: '情景 1 (-2%)', profitAdjust: -0.02, policyAdjust: -0.03 },
  { id: 's2', name: '情景 2 (-1%)', profitAdjust: -0.01, policyAdjust: -0.015 },
  { id: 'base', name: '基准情景', profitAdjust: 0, policyAdjust: 0 },
  { id: 's4', name: '情景 4 (+1%)', profitAdjust: 0.01, policyAdjust: 0.015 },
  { id: 's5', name: '情景 5 (+2%)', profitAdjust: 0.02, policyAdjust: 0.03 }
]

// 业务单元数据
const businessUnits = ref([])

// 从业务单元划分页面加载数据
onMounted(() => {
  const selectedUnits = sessionStorage.getItem('selectedBusinessUnits')
  if (selectedUnits) {
    const selectedIds = JSON.parse(selectedUnits)
    const allUnits = [
      {
        unit_id: 'BU001',
        unit_name: '燃油车 - 续保',
        policy_count: 5000,
        avg_premium: 3500,
        total_premium: 17500000,
        expected_profit: 570000,
        profit_margin: 0.06,
        selectedScenario: 'base'
      },
      {
        unit_id: 'BU002',
        unit_name: '燃油车 - 新保',
        policy_count: 2000,
        avg_premium: 4800,
        total_premium: 9600000,
        expected_profit: 100000,
        profit_margin: 0.03,
        selectedScenario: 'base'
      },
      {
        unit_id: 'BU003',
        unit_name: '新能源 - 高价值',
        policy_count: 1500,
        avg_premium: 5800,
        total_premium: 8700000,
        expected_profit: 250000,
        profit_margin: 0.05,
        selectedScenario: 'base'
      },
      {
        unit_id: 'BU004',
        unit_name: '新能源 - 普通',
        policy_count: 3000,
        avg_premium: 4500,
        total_premium: 13500000,
        expected_profit: 150000,
        profit_margin: 0.035,
        selectedScenario: 'base'
      },
      {
        unit_id: 'BU005',
        unit_name: '豪车 - 续保',
        policy_count: 500,
        avg_premium: 15000,
        total_premium: 7500000,
        expected_profit: 450000,
        profit_margin: 0.08,
        selectedScenario: 'base'
      }
    ]
    businessUnits.value = allUnits.filter(unit => selectedIds.includes(unit.unit_id))
  }
})

// 计算属性 - 基于基准数据计算
const totalPolicyCount = computed(() => {
  return businessUnits.value.reduce((sum, unit) => sum + (unit.policy_count || 0), 0)
})

const totalPremium = computed(() => {
  return businessUnits.value.reduce((sum, unit) => sum + (unit.total_premium || 0), 0)
})

const totalExpectedProfit = computed(() => {
  return businessUnits.value.reduce((sum, unit) => sum + (unit.expected_profit || 0), 0)
})

const avgProfitMargin = computed(() => {
  if (businessUnits.value.length === 0) return 0
  const totalPremiumVal = totalPremium.value
  if (totalPremiumVal === 0) return 0
  return totalExpectedProfit.value / totalPremiumVal
})

// 情景计算
const calculateScenarioPolicyCount = (unit, scenarioId) => {
  const scenario = scenarios.find(s => s.id === scenarioId)
  if (!scenario) return unit.policy_count
  return Math.round(unit.policy_count * (1 + scenario.policyAdjust))
}

const calculateScenarioPremium = (unit, scenarioId) => {
  const scenario = scenarios.find(s => s.id === scenarioId)
  if (!scenario) return unit.total_premium
  return Math.round(unit.total_premium * (1 + scenario.policyAdjust))
}

const calculateScenarioProfit = (unit, scenarioId) => {
  const scenario = scenarios.find(s => s.id === scenarioId)
  if (!scenario) return unit.expected_profit
  return Math.round(unit.expected_profit * (1 + scenario.profitAdjust))
}

const calculateScenarioMargin = (unit, scenarioId) => {
  const profit = calculateScenarioProfit(unit, scenarioId)
  const premium = calculateScenarioPremium(unit, scenarioId)
  if (premium === 0) return 0
  return profit / premium
}

// 方法
const toggleExpand = (index) => {
  const pos = expandedRows.value.indexOf(index)
  if (pos === -1) {
    expandedRows.value.push(index)
  } else {
    expandedRows.value.splice(pos, 1)
  }
}

const selectScenario = (unit, scenarioId) => {
  unit.selectedScenario = scenarioId
}

const applyScenario = (unit) => {
  const scenario = scenarios.find(s => s.id === unit.selectedScenario)
  if (scenario) {
    unit.policy_count = calculateScenarioPolicyCount(unit, unit.selectedScenario)
    unit.total_premium = calculateScenarioPremium(unit, unit.selectedScenario)
    unit.expected_profit = calculateScenarioProfit(unit, unit.selectedScenario)
    unit.profit_margin = calculateScenarioMargin(unit, unit.selectedScenario)
    
    ElMessage.success(`已应用${scenario.name}`)
    expandedRows.value = []
  }
}

const handleBack = () => {
  router.push('/admin/cost-simulation')
}

const handleTempSave = () => {
  ElMessage.success('策略已暂时保存')
}

const handleSave = () => {
  saveDialogVisible.value = true
}

const confirmSave = () => {
  if (!strategyForm.name) {
    ElMessage.warning('请输入策略名称')
    return
  }

  // 保存策略到 sessionStorage
  const strategy = {
    id: 'strategy_' + Date.now(),
    name: strategyForm.name,
    description: strategyForm.description,
    business_units: businessUnits.value,
    created_at: new Date().toISOString(),
    status: 'draft'
  }

  // 获取已保存的策略列表
  const savedStrategies = JSON.parse(sessionStorage.getItem('savedStrategies') || '[]')
  savedStrategies.push(strategy)
  sessionStorage.setItem('savedStrategies', JSON.stringify(savedStrategies))
  
  // 记录保存时间，用于刷新策略总览
  sessionStorage.setItem('lastStrategySaveTime', Date.now().toString())

  ElMessage.success('策略已保存')
  saveDialogVisible.value = false
  
  // 跳转到策略总览
  setTimeout(() => {
    router.push('/admin/strategy-overview')
  }, 500)
}

const exportReport = () => {
  ElMessage.info('导出功能开发中')
}

const getMarginClass = (margin) => {
  if (margin >= 0.06) return 'high'
  if (margin >= 0.03) return 'medium'
  if (margin >= 0) return 'low'
  return 'negative'
}

// 整体测算
const calculateAll = () => {
  // 重新计算所有业务单元的预估数据
  businessUnits.value.forEach(unit => {
    // 计算纯风险成本 RP = 平均保费 × 目标赔付率 (假设 75%)
    unit.rp = (unit.avg_premium || 3500) * 0.75
    // 重新计算预期利润
    unit.expected_profit = (unit.policy_count || 0) * (unit.avg_premium || 3500) * (unit.profit_margin || 0.05)
  })
  ElMessage.success('整体测算完成')
}
</script>

<style scoped>
.revenue-simulation-page {
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
  font-size: 12px;
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

.header-actions {
  display: flex;
  gap: 8px;
}

.section-indicator {
  width: 6px;
  height: 24px;
  background: #712ae2;
  border-radius: 3px;
}

.section-indicator.primary {
  background: #002d81;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.scenario-tab {
  padding: 8px 16px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  color: #606266;
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
  padding: 10px 12px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
  white-space: nowrap;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  font-size: 13px;
}

.table-row:hover {
  background: #f5f7fa;
}

.expand-btn {
  background: transparent;
  border: none;
  color: #909399;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.expand-btn:hover {
  background: #e4e7ed;
  color: #303133;
}

.expand-btn.expanded {
  color: #002d81;
}

.unit-name-cell {
  font-weight: 600;
  color: #303133;
}

.number {
  font-family: 'Segoe UI', Arial, sans-serif;
  font-weight: 600;
  color: #303133;
}

.profit-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.profit-badge.positive {
  background: #f0f9eb;
  color: #67c23a;
}

.profit-badge.negative {
  background: #fef0f0;
  color: #f56c6c;
}

.margin-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
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

.profit-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.profit-badge.positive {
  background: #f0f9eb;
  color: #67c23a;
}

.profit-badge.negative {
  background: #fef0f0;
  color: #f56c6c;
}

.scenario-btn {
  background: transparent;
  border: none;
  color: #002d81;
  font-size: 13px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
  font-weight: 600;
  transition: all 0.2s;
}

.scenario-btn:hover {
  background: #f5f7fa;
}

/* 展开内容 */
.expand-row {
  background: #fafafa;
}

.expand-content {
  padding: 0;
}

.scenario-panel {
  padding: 20px;
}

.scenario-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.scenario-tab {
  padding: 8px 16px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  color: #606266;
}

.scenario-tab:hover {
  color: #002d81;
  border-color: #c6e2ff;
}

.scenario-tab.active {
  background: #002d81;
  color: white;
  border-color: #002d81;
}

.scenario-summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.summary-box {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  text-align: center;
}

.summary-box-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
}

.summary-box-value {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.summary-box-value.positive {
  color: #67c23a;
}

.summary-box-value.negative {
  color: #f56c6c;
}

/* 五情景对比表格 */
.scenario-comparison-table {
  margin-bottom: 16px;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.comparison-item {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.comparison-item.selected {
  border-color: #002d81;
  box-shadow: 0 2px 8px rgba(0, 45, 129, 0.15);
}

.comparison-header {
  padding: 10px;
  background: #f5f7fa;
  font-size: 11px;
  font-weight: 600;
  color: #606266;
  text-align: center;
  border-bottom: 1px solid #ebeef5;
}

.comparison-item.selected .comparison-header {
  background: #002d81;
  color: white;
}

.comparison-data {
  padding: 16px 12px;
}

.data-row {
  margin-bottom: 12px;
  text-align: center;
}

.data-row:last-child {
  margin-bottom: 0;
}

.data-label {
  display: block;
  font-size: 10px;
  color: #909399;
  margin-bottom: 4px;
}

.data-value {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: #303133;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.data-value.highlight {
  color: #002d81;
}

.data-value-small {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.data-value-small.highlight {
  color: #002d81;
}

.scenario-actions {
  text-align: right;
}

/* 汇总区域 */
.summary-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  border-left: 4px solid #002d81;
}

.summary-section .section-header {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 16px;
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
  padding: 24px;
  text-align: center;
}

.summary-item-label {
  font-size: 11px;
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

.summary-item-value.positive {
  color: #67c23a;
}

.summary-item-value.negative {
  color: #f56c6c;
}

.summary-unit {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}

.summary-percent {
  font-size: 18px;
  font-weight: 600;
  color: #909399;
}

.status-tag {
  margin-left: 8px;
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

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
}

.icon {
  margin-right: 4px;
}
</style>
