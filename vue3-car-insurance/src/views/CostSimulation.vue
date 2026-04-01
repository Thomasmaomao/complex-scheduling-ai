<template>
  <div class="cost-simulation-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1>步骤 2：成本模拟</h1>
        <p class="description">配置全局兜底参数，支持业务单元独立参数（优先级更高）</p>
      </div>
    </div>

    <!-- 步骤进度条 -->
    <div class="steps-container">
      <div class="step-item">
        <div class="step-icon">1</div>
        <div class="step-label">业务单元</div>
      </div>
      <div class="step-line"></div>
      <div class="step-item active">
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

    <!-- 全局兜底参数 - 紧凑布局 (3 列 x2 行) -->
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <h3>统一策略参数</h3>
          <span class="param-note">Global Parameters</span>
          <div class="card-actions">
            <el-button type="primary" size="small" @click="calculateAll">
              <span class="icon">🔢</span> 批量测算
            </el-button>
          </div>
        </div>
      </template>

      <div class="global-params-compact">
        <div class="param-item">
          <label class="param-label">固定成本率</label>
          <div class="input-with-suffix">
            <el-input 
              v-model="globalParams.fixed_cost_ratio" 
              type="number"
              :precision="4" 
              :step="0.01" 
              :min="0" 
              :max="1" 
              @input="handleGlobalParamChange"
            />
            <span class="input-suffix">%</span>
          </div>
        </div>
        
        <div class="param-item">
          <label class="param-label">目标赔付率</label>
          <div class="input-with-suffix">
            <el-input 
              v-model="globalParams.target_loss_ratio" 
              type="number"
              :precision="4" 
              :step="0.01" 
              :min="0" 
              :max="1" 
              @input="handleGlobalParamChange"
            />
            <span class="input-suffix">%</span>
          </div>
        </div>
        
        <div class="param-item">
          <label class="param-label">市场费用率</label>
          <div class="input-with-suffix">
            <el-input 
              v-model="globalParams.market_expense_ratio" 
              type="number"
              :precision="4" 
              :step="0.01" 
              :min="0" 
              :max="1" 
              @input="handleGlobalParamChange"
            />
            <span class="input-suffix">%</span>
          </div>
        </div>
        
        <div class="param-item">
          <label class="param-label">自主系数下限</label>
          <div class="input-with-suffix">
            <el-input 
              v-model="globalParams.autonomous_discount_min" 
              type="number"
              :precision="2" 
              :step="0.01" 
              :min="0.5" 
              :max="1.5"
              @input="handleGlobalParamChange"
            />
            <span class="input-suffix"></span>
          </div>
        </div>
        
        <div class="param-item">
          <label class="param-label">自主系数上限</label>
          <div class="input-with-suffix">
            <el-input 
              v-model="globalParams.autonomous_discount_max" 
              type="number"
              :precision="2" 
              :step="0.01" 
              :min="0.5" 
              :max="1.5"
              @input="handleGlobalParamChange"
            />
            <span class="input-suffix"></span>
          </div>
        </div>
        
        <div class="param-item checkbox-item">
          <label class="checkbox-label">
            <el-checkbox v-model="globalParams.is_calculate" @change="handleGlobalParamChange" />
            <span>反算折扣</span>
          </label>
        </div>
      </div>
    </el-card>

    <!-- 业务单元成本模拟表格 -->
    <div class="table-section">
      <div class="table-header">
        <h3>业务单元成本模拟</h3>
        <div class="table-actions">
          <el-button size="small" @click="exportReport">导出报告</el-button>
        </div>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>业务单元</th>
              <th class="text-right">保单数</th>
              <th class="text-right">平均保费</th>
              <th class="text-right">保费规模</th>
              <th class="text-right">纯风险成本</th>
              <th class="text-right">预期利润率</th>
              <th class="text-center">使用全局参数</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="unit in businessUnits" :key="unit.unit_id" class="table-row">
              <td>
                <div class="unit-name">{{ unit.unit_name }}</div>
                <div class="unit-name-en">{{ unit.unit_name_en || '-' }}</div>
              </td>
              <td class="text-right number">{{ unit.policy_count?.toLocaleString() }}</td>
              <td class="text-right number">¥{{ unit.avg_premium?.toLocaleString() }}</td>
              <td class="text-right number">¥{{ ((unit.policy_count || 0) * (unit.avg_premium || 0) / 10000).toFixed(0) }}万</td>
              <td class="text-right number">¥{{ (unit.rp || 0).toFixed(0) }}</td>
              <td class="text-right">
                <span :class="['margin-badge', getMarginClass(unit.profit_margin)]">
                  {{ ((unit.profit_margin || 0) * 100).toFixed(1) }}%
                </span>
              </td>
              <td class="text-center">
                <el-tag :type="unit.fixed_cost_ratio === null ? 'success' : 'info'" size="small">
                  {{ unit.fixed_cost_ratio === null ? '是' : '否' }}
                </el-tag>
              </td>
              <td class="text-center">
                <button class="edit-btn" @click="editUnit(unit)">
                  <span class="icon">✏️</span> 编辑
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 整体汇总结果 -->
    <el-card class="summary-card" v-if="businessUnits.length > 0">
      <div class="summary-content">
        <div class="summary-label">总利润预算 (估计)</div>
        <div class="summary-value">¥{{ (totalExpectedProfit / 10000).toFixed(2) }}万</div>
      </div>
    </el-card>

    <!-- 底部操作按钮 -->
    <div class="footer-actions">
      <el-button @click="handleBack">上一步：业务单元</el-button>
      <div class="footer-right">
        <el-button type="primary" @click="handleNext">下一步：收益模拟</el-button>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editDialogVisible" title="业务单元参数配置" width="600px">
      <el-form :model="currentUnit" label-width="120px">
        <el-form-item label="业务单元">
          <span class="dialog-unit-name">{{ currentUnit.unit_name }}</span>
        </el-form-item>
        
        <el-form-item label="固定成本率">
          <el-input-number 
            v-model="currentUnit.fixed_cost_ratio" 
            :precision="4" 
            :step="0.01" 
            :min="0" 
            :max="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="目标赔付率">
          <el-input-number 
            v-model="currentUnit.target_loss_ratio" 
            :precision="4" 
            :step="0.01" 
            :min="0" 
            :max="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="市场费用率">
          <el-input-number 
            v-model="currentUnit.market_expense_ratio" 
            :precision="4" 
            :step="0.01" 
            :min="0" 
            :max="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="自主系数区间">
          <div class="range-form-item">
            <el-input-number 
              v-model="currentUnit.autonomous_discount_min" 
              :precision="2" 
              :step="0.01" 
              :min="0.5" 
              :max="1.5"
              controls-position="right"
            />
            <span class="range-text">至</span>
            <el-input-number 
              v-model="currentUnit.autonomous_discount_max" 
              :precision="2" 
              :step="0.01" 
              :min="0.5" 
              :max="1.5"
              controls-position="right"
            />
          </div>
        </el-form-item>
        
        <el-form-item label="反算折扣">
          <el-radio-group v-model="currentUnit.is_calculate">
            <el-radio :label="true">是</el-radio>
            <el-radio :label="false">否</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUnitParams">保存并测算</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const editDialogVisible = ref(false)
const currentUnit = ref({})

// 全局兜底参数
const globalParams = reactive({
  fixed_cost_ratio: 0.10,
  target_loss_ratio: 0.75,
  market_expense_ratio: 0.12,
  autonomous_discount_min: 0.50,
  autonomous_discount_max: 0.65,
  is_calculate: true
})

// 业务单元数据
const businessUnits = ref([])

// 计算属性
const totalPolicyCount = computed(() => {
  return businessUnits.value.reduce((sum, unit) => sum + (unit.policy_count || 0), 0)
})

const totalPremium = computed(() => {
  return businessUnits.value.reduce((sum, unit) => sum + (unit.policy_count || 0) * (unit.avg_premium || 0), 0)
})

const totalExpectedProfit = computed(() => {
  return businessUnits.value.reduce((sum, unit) => sum + (unit.expected_profit || 0), 0)
})

const avgProfitMargin = computed(() => {
  if (businessUnits.value.length === 0) return 0
  const total = businessUnits.value.reduce((sum, unit) => sum + (unit.profit_margin || 0), 0)
  return total / businessUnits.value.length
})

// 加载数据
onMounted(() => {
  const selectedUnits = sessionStorage.getItem('selectedBusinessUnits')
  if (selectedUnits) {
    const selectedIds = JSON.parse(selectedUnits)
    const allUnits = [
      {
        unit_id: 'BU001',
        unit_name: '燃油车 - 续保',
        unit_name_en: 'Conventional - Renewal',
        policy_count: 5000,
        avg_premium: 3500,
        autonomous_discount: 0.53,
        rp: 2520,
        expected_profit: 570000,
        profit_margin: 0.06,
        fixed_cost_ratio: null,
        target_loss_ratio: null,
        market_expense_ratio: null,
        autonomous_discount_min: null,
        autonomous_discount_max: null,
        is_calculate: null
      },
      {
        unit_id: 'BU002',
        unit_name: '燃油车 - 新保',
        unit_name_en: 'Conventional - New',
        policy_count: 2000,
        avg_premium: 4800,
        autonomous_discount: 1.03,
        rp: 3600,
        expected_profit: 100000,
        profit_margin: 0.03,
        fixed_cost_ratio: null,
        target_loss_ratio: null,
        market_expense_ratio: null,
        autonomous_discount_min: null,
        autonomous_discount_max: null,
        is_calculate: null
      },
      {
        unit_id: 'BU003',
        unit_name: '新能源 - 高价值',
        unit_name_en: 'NEV - Premium',
        policy_count: 1500,
        avg_premium: 5800,
        autonomous_discount: 0.85,
        rp: 4350,
        expected_profit: 250000,
        profit_margin: 0.045,
        fixed_cost_ratio: null,
        target_loss_ratio: null,
        market_expense_ratio: null,
        autonomous_discount_min: null,
        autonomous_discount_max: null,
        is_calculate: null
      },
      {
        unit_id: 'BU004',
        unit_name: '新能源 - 普通',
        unit_name_en: 'NEV - Standard',
        policy_count: 3000,
        avg_premium: 4500,
        autonomous_discount: 0.95,
        rp: 3510,
        expected_profit: 150000,
        profit_margin: 0.035,
        fixed_cost_ratio: null,
        target_loss_ratio: null,
        market_expense_ratio: null,
        autonomous_discount_min: null,
        autonomous_discount_max: null,
        is_calculate: null
      },
      {
        unit_id: 'BU005',
        unit_name: '豪车 - 续保',
        unit_name_en: 'Luxury - Renewal',
        policy_count: 500,
        avg_premium: 15000,
        autonomous_discount: 1.20,
        rp: 10200,
        expected_profit: 450000,
        profit_margin: 0.08,
        fixed_cost_ratio: null,
        target_loss_ratio: null,
        market_expense_ratio: null,
        autonomous_discount_min: null,
        autonomous_discount_max: null,
        is_calculate: null
      }
    ]
    businessUnits.value = allUnits.filter(unit => selectedIds.includes(unit.unit_id))
    
    // 初始化计算
    businessUnits.value.forEach(unit => {
      calculateRow(unit)
    })
  }
})

// 获取实际使用的参数（独立参数优先）
const getEffectiveParams = (unit) => {
  if (unit.fixed_cost_ratio !== null && unit.fixed_cost_ratio !== undefined) {
    return {
      fixed_cost_ratio: unit.fixed_cost_ratio,
      target_loss_ratio: unit.target_loss_ratio,
      market_expense_ratio: unit.market_expense_ratio,
      autonomous_discount_min: unit.autonomous_discount_min,
      autonomous_discount_max: unit.autonomous_discount_max,
      is_calculate: unit.is_calculate
    }
  }
  
  return globalParams
}

// 计算利润
const calculateProfit = (unit) => {
  const params = getEffectiveParams(unit)
  
  // 计算自主系数 = (下限 + 上限) / 2
  const autonomous_discount = (params.autonomous_discount_min + params.autonomous_discount_max) / 2
  
  // 计算利润率 = 1 - 固定成本率 - 目标赔付率 - 市场费用率
  const profit_margin = 1 - params.fixed_cost_ratio - params.target_loss_ratio - params.market_expense_ratio
  
  // 计算预期利润 = 保单数 × 平均保费 × 利润率
  const total_premium = unit.policy_count * unit.avg_premium
  const expected_profit = total_premium * profit_margin
  
  // 计算 RP(纯风险保费) = 平均保费 × 目标赔付率
  const rp = unit.avg_premium * params.target_loss_ratio
  
  return {
    autonomous_discount,
    expected_profit,
    profit_margin,
    rp
  }
}

// 计算单行
const calculateRow = (unit) => {
  const result = calculateProfit(unit)
  unit.autonomous_discount = result.autonomous_discount
  unit.expected_profit = result.expected_profit
  unit.profit_margin = result.profit_margin
  unit.rp = result.rp
}

// 全局参数变化处理
const handleGlobalParamChange = () => {
  businessUnits.value.forEach(unit => {
    if (unit.fixed_cost_ratio === null || unit.fixed_cost_ratio === undefined) {
      calculateRow(unit)
    }
  })
}

// 编辑业务单元
const editUnit = (unit) => {
  currentUnit.value = { ...unit }
  editDialogVisible.value = true
}

// 保存业务单元参数
const saveUnitParams = () => {
  const index = businessUnits.value.findIndex(u => u.unit_id === currentUnit.value.unit_id)
  if (index !== -1) {
    businessUnits.value[index] = {
      ...businessUnits.value[index],
      fixed_cost_ratio: currentUnit.value.fixed_cost_ratio,
      target_loss_ratio: currentUnit.value.target_loss_ratio,
      market_expense_ratio: currentUnit.value.market_expense_ratio,
      autonomous_discount_min: currentUnit.value.autonomous_discount_min,
      autonomous_discount_max: currentUnit.value.autonomous_discount_max,
      is_calculate: currentUnit.value.is_calculate
    }
    calculateRow(businessUnits.value[index])
  }
  editDialogVisible.value = false
  ElMessage.success('参数已保存')
}

// 整体测算
const calculateAll = () => {
  businessUnits.value.forEach(unit => {
    calculateRow(unit)
  })
  ElMessage.success('模拟测算完成')
}

// 导出报告
const exportReport = () => {
  ElMessage.info('导出功能开发中')
}

// 导航
const handleBack = () => {
  router.push('/admin/business-unit')
}

const handleNext = () => {
  router.push('/admin/revenue-simulation')
}

// 工具函数
const formatCurrency = (value) => {
  if (value === null || value === undefined) return '0'
  return (value / 10000).toFixed(0)
}

// 获取利润率样式类
const getMarginClass = (margin) => {
  if (!margin) return 'low'
  if (margin >= 0.06) return 'high'
  if (margin >= 0.03) return 'medium'
  if (margin >= 0) return 'low'
  return 'negative'
}
</script>

<style scoped>
.cost-simulation-page {
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
  font-size: 11px;
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

/* 卡片样式 */
.config-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  border-left: 4px solid #002d81;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.param-note {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.card-actions {
  margin-left: auto;
}

/* 全局参数网格 - 紧凑布局 (3 列 x2 行) */
.global-params-compact {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px 20px;
  padding: 16px 20px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.param-label {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
}

.input-with-suffix {
  position: relative;
}

.input-with-suffix :deep(.el-input__wrapper) {
  border-radius: 6px;
}

.input-suffix {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #909399;
  font-size: 13px;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-inputs :deep(.el-input__wrapper) {
  border-radius: 6px;
}

.range-separator {
  color: #909399;
}

.checkbox-item {
  justify-content: flex-end;
  padding-top: 20px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  cursor: pointer;
}

/* 表格区域 */
.table-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.table-actions {
  display: flex;
  gap: 8px;
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

.unit-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.unit-name-en {
  font-size: 10px;
  color: #909399;
  text-transform: uppercase;
}

.number {
  font-family: 'Segoe UI', Arial, sans-serif;
  font-weight: 600;
  color: #303133;
}

.coefficient-badge {
  display: inline-block;
  padding: 4px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  font-family: 'Segoe UI', Arial, sans-serif;
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

.profit-value {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  font-weight: 600;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.profit-value.positive {
  color: #67c23a;
}

.profit-value.negative {
  color: #f56c6c;
}

.profit-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.profit-dot.positive {
  background: #67c23a;
  box-shadow: 0 0 8px rgba(103, 194, 58, 0.6);
}

.profit-dot.negative {
  background: #f56c6c;
  box-shadow: 0 0 8px rgba(245, 108, 108, 0.6);
}

.edit-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: transparent;
  border: none;
  color: #712ae2;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: #f5f7fa;
}

.edit-btn .icon {
  font-size: 14px;
}

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
}

/* 汇总卡片 */
.summary-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.summary-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%);
  border-radius: 8px;
}

.summary-label {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  font-weight: 600;
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  font-family: 'Segoe UI', Arial, sans-serif;
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

/* 弹窗样式 */
.dialog-unit-name {
  font-weight: 600;
  color: #303133;
}

.range-form-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.range-text {
  color: #909399;
  font-size: 13px;
}

/* 弹窗样式 */
.dialog-unit-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}
</style>
