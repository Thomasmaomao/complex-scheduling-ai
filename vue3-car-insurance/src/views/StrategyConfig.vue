<template>
  <div class="strategy-config-page">
    <div class="page-header">
      <h1>⚙️ 策略配置中心</h1>
      <p>配置智能推荐策略的优先级权重和阈值规则</p>
    </div>

    <!-- 策略列表 -->
    <el-card class="strategy-list-card">
      <template #header>
        <div class="card-header">
          <h3>策略列表</h3>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建策略
          </el-button>
        </div>
      </template>

      <el-table :data="strategies" stripe style="width: 100%">
        <el-table-column prop="strategy_id" label="策略 ID" width="150" />
        <el-table-column prop="strategy_name" label="策略名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="250" />
        <!-- 问题 5：统一使用 status 字段，isActive 作为显示属性 -->
        <el-table-column prop="isActive" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isActive ? 'success' : 'info'">
              {{ row.isActive ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" @click="handleTest(row)">测试</el-button>
            <el-button 
              size="small" 
              :type="row.isActive ? 'warning' : 'success'"
              @click="handleToggleStatus(row)"
            >
              {{ row.isActive ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 策略配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建策略' : '编辑策略'"
      width="800px"
    >
      <el-form :model="currentStrategy" label-width="140px">
        <el-form-item label="策略 ID" required>
          <el-input v-model="currentStrategy.strategy_id" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item label="策略名称" required>
          <el-input v-model="currentStrategy.strategy_name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="currentStrategy.description" type="textarea" :rows="3" />
        </el-form-item>

        <el-divider content-position="left">优先级权重配置</el-divider>
        <el-form-item label="价格权重" required>
          <el-slider v-model="currentStrategy.priority_weights.price" :min="0" :max="100" show-input />
          <el-text type="info">推荐值：40</el-text>
        </el-form-item>
        <el-form-item label="服务权重" required>
          <el-slider v-model="currentStrategy.priority_weights.service" :min="0" :max="100" show-input />
          <el-text type="info">推荐值：35</el-text>
        </el-form-item>
        <el-form-item label="赔付权重" required>
          <el-slider v-model="currentStrategy.priority_weights.claim" :min="0" :max="100" show-input />
          <el-text type="info">推荐值：25</el-text>
        </el-form-item>

        <el-alert
          v-if="weightSum !== 100"
          title="权重总和必须为 100"
          type="warning"
          :closable="false"
          show-icon
        />

        <el-divider content-position="left">阈值规则配置</el-divider>
        <el-form-item label="最低价格得分">
          <el-input-number v-model="currentStrategy.threshold_rules.min_price_score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="最低服务得分">
          <el-input-number v-model="currentStrategy.threshold_rules.min_service_score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="最低赔付得分">
          <el-input-number v-model="currentStrategy.threshold_rules.min_claim_score" :min="0" :max="100" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :disabled="weightSum !== 100">保存</el-button>
      </template>
    </el-dialog>

    <!-- 策略测试对话框 -->
    <el-dialog v-model="testDialogVisible" title="策略测试" width="900px">
      <el-form label-width="120px">
        <el-form-item label="测试策略">
          <el-select v-model="testStrategyId" style="width: 300px">
            <el-option
              v-for="strategy in strategies"
              :key="strategy.strategy_id"
              :label="strategy.strategy_name"
              :value="strategy.strategy_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="测试用例数">
          <el-input-number v-model="testCaseCount" :min="1" :max="100" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="runTest" :loading="testRunning">开始测试</el-button>
        </el-form-item>
      </el-form>

      <!-- 测试结果 -->
      <div v-if="testResult" class="test-result">
        <el-descriptions title="测试结果" :column="2" border>
          <el-descriptions-item label="测试 ID">{{ testResult.test_id }}</el-descriptions-item>
          <el-descriptions-item label="测试用例数">{{ testResult.total_cases }}</el-descriptions-item>
          <el-descriptions-item label="通过用例数">{{ testResult.passed_cases }}</el-descriptions-item>
          <el-descriptions-item label="失败用例数">{{ testResult.failed_cases }}</el-descriptions-item>
          <el-descriptions-item label="通过率">
            <el-progress :percentage="testResult.pass_rate" :color="getPassRateColor(testResult.pass_rate)" />
          </el-descriptions-item>
        </el-descriptions>

        <el-table :data="testResult.details" style="margin-top: 20px" max-height="300">
          <el-table-column prop="case_id" label="用例 ID" width="150" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'passed' ? 'success' : 'danger'">
                {{ row.status === 'passed' ? '通过' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="quotes_count" label="报价数量" width="100" />
          <el-table-column prop="error" label="错误信息" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getAllStrategies, createStrategy, updateStrategy, updateStrategyStatus } from '../api/strategy'
// 公共策略加载工具函数
import { loadStrategiesForUI, transformStrategyToBackend } from '../utils/strategy-transform'

// 配置常量（必须在变量声明前定义）
const DEFAULT_AUTONOMOUS_DISCOUNT = {
  min: 0.50,
  max: 0.65
}

const DEFAULT_THRESHOLD_RULES = {
  min_price_score: 60,
  min_service_score: 70,
  min_claim_score: 60
}

// 策略列表
const strategies = ref([])

// 对话框
const dialogVisible = ref(false)
const dialogMode = ref('create')
// 问题 5：统一使用 status 字段，isActive 作为显示属性
const currentStrategy = reactive({
  strategy_id: '',
  strategy_name: '',
  description: '',
  priority_weights: { price: 40, service: 35, claim: 25 },
  // 问题 4 & 8：使用配置常量
  threshold_rules: { ...DEFAULT_THRESHOLD_RULES },
  autonomous_discount_min: DEFAULT_AUTONOMOUS_DISCOUNT.min,
  autonomous_discount_max: DEFAULT_AUTONOMOUS_DISCOUNT.max,
  status: 'draft',
  isActive: true,
})

// 权重总和
const weightSum = computed(() => {
  return (
    currentStrategy.priority_weights.price +
    currentStrategy.priority_weights.service +
    currentStrategy.priority_weights.claim
  )
})

// 测试对话框
const testDialogVisible = ref(false)
const testStrategyId = ref('default_v1')
const testCaseCount = ref(10)
const testRunning = ref(false)
const testResult = ref(null)

// 生命周期
onMounted(() => {
  loadStrategies()
})

// 方法
const loadStrategies = async () => {
  try {
    // 使用公共工具函数加载并转换策略数据
    const strategiesData = await loadStrategiesForUI({
      onError: (error) => {
        ElMessage.error('加载策略失败：' + error.message)
      }
    })
    
    // 转换为 StrategyConfig 组件需要的格式
    strategies.value = strategiesData.map(strategy => ({
      strategy_id: strategy.id,
      strategy_name: strategy.name,
      description: strategy.description,
      priority_weights: strategy.priority_weights,
      // 问题 4：使用配置常量而非硬编码
      threshold_rules: { ...DEFAULT_THRESHOLD_RULES },
      // 问题 5：统一使用 status 字段，isActive 作为计算属性
      status: strategy.status,
      isActive: strategy.status !== 'archived',
      institutions: strategy.institutions,
      business_units: strategy.businessUnits
    }))
  } catch (error) {
    // 错误已在工具函数中处理
    console.error('加载策略失败:', error)
  }
}

const handleCreate = () => {
  dialogMode.value = 'create'
  Object.assign(currentStrategy, {
    strategy_id: '',
    strategy_name: '',
    description: '',
    priority_weights: { price: 40, service: 35, claim: 25 },
    // 问题 4 & 8：使用配置常量
    threshold_rules: { ...DEFAULT_THRESHOLD_RULES },
    autonomous_discount_min: DEFAULT_AUTONOMOUS_DISCOUNT.min,
    autonomous_discount_max: DEFAULT_AUTONOMOUS_DISCOUNT.max,
    status: 'draft',
    isActive: true,
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogMode.value = 'edit'
  // 问题 5：统一使用 status 字段
  Object.assign(currentStrategy, {
    strategy_id: row.strategy_id,
    strategy_name: row.strategy_name,
    description: row.description,
    priority_weights: { ...row.priority_weights },
    threshold_rules: { ...row.threshold_rules },
    status: row.status,
    isActive: row.status !== 'archived',
    institutions: row.institutions || [],
    business_units: row.business_units || []
  })
  dialogVisible.value = true
}

// 问题 4 & 8：保存策略处理函数 - 使用公共转换函数和配置常量
const handleSave = async () => {
  try {
    // 使用公共转换函数，避免重复逻辑
    const strategyData = transformStrategyToBackend({
      strategy_name: currentStrategy.strategy_name,
      description: currentStrategy.description,
      priority_weights: currentStrategy.priority_weights,
      autonomous_discount_min: DEFAULT_AUTONOMOUS_DISCOUNT.min,
      autonomous_discount_max: DEFAULT_AUTONOMOUS_DISCOUNT.max,
      institutions: currentStrategy.institutions || [],
      businessUnits: currentStrategy.business_units || []
    })
    
    if (dialogMode.value === 'create') {
      const response = await createStrategy(strategyData)
      ElMessage.success('策略创建成功')
    } else {
      const strategyId = currentStrategy.strategy_id
      await updateStrategy(strategyId, strategyData)
      ElMessage.success('策略更新成功')
    }
    
    dialogVisible.value = false
    loadStrategies()
  } catch (error) {
    console.error('保存策略失败:', error)
    ElMessage.error('保存策略失败：' + (error.response?.data?.detail || error.message))
  }
}

const handleToggleStatus = async (row) => {
  // 问题 5：统一使用 status 字段
  const newStatus = row.isActive ? 'archived' : 'draft'
  try {
    await updateStrategyStatus(row.strategy_id, newStatus)
    row.status = newStatus
    row.isActive = !row.isActive
    ElMessage.success(`策略已${row.isActive ? '启用' : '禁用'}`)
  } catch (error) {
    ElMessage.error('切换状态失败：' + (error.response?.data?.detail || error.message))
    // 恢复原状态
    row.status = newStatus === 'archived' ? 'draft' : 'archived'
    row.isActive = !row.isActive
  }
}

const handleTest = (row) => {
  testStrategyId.value = row.strategy_id
  testDialogVisible.value = true
  testResult.value = null
}

const runTest = async () => {
  testRunning.value = true
  try {
    // TODO: 后端测试 API 实现后启用
    // const response = await recordTestResult(testStrategyId.value, {...})
    // testResult.value = response.data
    
    ElMessage.info('测试功能开发中，请稍后...')
  } catch (error) {
    ElMessage.error('测试失败：' + (error.response?.data?.detail || error.message))
  } finally {
    testRunning.value = false
  }
}

const getPassRateColor = (rate) => {
  if (rate >= 95) return '#67c23a'
  if (rate >= 80) return '#409eff'
  return '#f56c6c'
}
</script>

<style scoped>
.strategy-config-page {
  padding: 24px;
  margin-left: 256px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-header p {
  color: #909399;
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.test-result {
  margin-top: 20px;
}
</style>
