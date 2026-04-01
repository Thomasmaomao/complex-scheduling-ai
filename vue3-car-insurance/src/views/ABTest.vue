<template>
  <div class="ab-test-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>策略测试中心 - A/B 测试</h1>
      <p>设计并执行 A/B 测试实验，科学验证策略效果</p>
    </div>

    <!-- 第 1 部分：实验设置表单 -->
    <el-card class="setup-card">
      <template #header>
        <div class="card-header">
          <h3>📝 实验设置</h3>
        </div>
      </template>

      <el-form :model="experiment" label-width="120px" size="default">
        <!-- 实验名称 -->
        <el-form-item label="实验名称" required>
          <el-input 
            v-model="experiment.name" 
            placeholder="例如：燃油车续保策略优化"
            style="max-width: 500px"
          />
        </el-form-item>

        <!-- 实验假设 -->
        <el-form-item label="实验假设" required>
          <el-input 
            v-model="experiment.hypothesis" 
            type="textarea" 
            :rows="2"
            placeholder="例如：降低自主系数，成交率提升>15% 且利润率不下降"
            style="max-width: 600px"
          />
        </el-form-item>

        <!-- 策略选择 -->
        <el-divider content-position="left">分组策略配置</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="对照组 (A)" required>
              <el-select v-model="experiment.control_strategy" placeholder="请选择对比基准" style="width: 100%">
                <el-option label="当前线上策略" value="current" />
                <el-option label="历史最优策略" value="best" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实验组 (B)" required>
              <el-select v-model="experiment.treatment_strategy" placeholder="请选择已保存的策略" style="width: 100%">
                <el-option
                  v-for="strategy in savedStrategies"
                  :key="strategy.id"
                  :label="strategy.name"
                  :value="strategy.id"
                >
                  <span>{{ strategy.name }}</span>
                  <span style="color: #909399; font-size: 12px; margin-left: 8px">{{ strategy.description }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 流量分配 -->
        <el-form-item label="流量分配" required>
          <div class="traffic-split-container">
            <el-slider 
              v-model="experiment.traffic_split" 
              :min="0" 
              :max="100"
              :step="10"
              :marks="{0: '0%', 50: '50%', 100: '100%'}"
              style="width: 300px"
            />
            <div class="traffic-labels">
              <span class="control-label">对照组 {{ 100 - experiment.traffic_split }}%</span>
              <span class="treatment-label">实验组 {{ experiment.traffic_split }}%</span>
            </div>
          </div>
        </el-form-item>

        <!-- 实验周期 -->
        <el-form-item label="实验周期" required>
          <el-input-number 
            v-model="experiment.duration_days" 
            :min="1" 
            :max="90"
            :step="1"
            style="width: 150px"
          />
          <span class="unit-text">天</span>
        </el-form-item>

        <!-- 适用机构 -->
        <el-form-item label="适用机构" required>
          <el-checkbox-group v-model="experiment.institutions">
            <el-checkbox label="上海" />
            <el-checkbox label="北京" />
            <el-checkbox label="广东" />
            <el-checkbox label="浙江" />
            <el-checkbox label="江苏" />
            <el-checkbox label="四川" />
          </el-checkbox-group>
        </el-form-item>

        <!-- 业务单元 -->
        <el-form-item label="业务单元" required>
          <el-checkbox-group v-model="experiment.business_units">
            <el-checkbox label="燃油车 - 续保" />
            <el-checkbox label="燃油车 - 新保" />
            <el-checkbox label="新能源 - 高价值" />
            <el-checkbox label="新能源 - 普通" />
            <el-checkbox label="豪车 - 续保" />
          </el-checkbox-group>
        </el-form-item>

        <!-- 实验描述 -->
        <el-form-item label="实验描述">
          <el-input 
            v-model="experiment.description" 
            type="textarea" 
            :rows="2"
            placeholder="请说明实验目的和预期效果（选填）"
            style="max-width: 600px"
          />
        </el-form-item>

        <!-- 影响范围说明 -->
        <el-alert
          :title="impactDescription"
          type="info"
          :closable="false"
          show-icon
          style="margin: 16px 0"
        />

        <!-- 提交按钮 -->
        <div class="form-actions">
          <el-button type="primary" size="default" @click="handleStartTest" :loading="starting">
            🚀 启动 A/B 测试
          </el-button>
        </div>
      </el-form>
    </el-card>

    <!-- 第 2 部分：实验结果（进行中/已完成） -->
    <el-card v-if="experimentRunning" class="result-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h3>📊 实验结果</h3>
          <el-tag :type="runningStatus.type" size="default">
            {{ runningStatus.icon }} {{ runningStatus.text }}
          </el-tag>
        </div>
      </template>

      <!-- 进度条 -->
      <div class="progress-section">
        <div class="progress-label">
          <span>进度：{{ progressPercentage }}% (第{{ currentDay }}天/{{ experiment.duration_days }}天)</span>
          <span v-if="isSignificant" class="significance-badge">✅ 统计显著性 p={{ pValue }}</span>
        </div>
        <el-progress 
          :percentage="progressPercentage" 
          :status="progressPercentage >= 100 ? 'success' : undefined"
          :stroke-width="12"
        />
      </div>

      <!-- 指标提升 -->
      <div class="metrics-summary">
        <div class="metric-item">
          <span class="metric-label">基准成交率</span>
          <span class="metric-value">{{ baseConversionRate.toFixed(2) }}%</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">成交率提升</span>
          <span :class="['metric-value', getMetricClass(conversionLift)]">
            {{ conversionLift > 0 ? '+' : '' }}{{ conversionLift.toFixed(2) }}%
          </span>
        </div>
        <div class="metric-item">
          <span class="metric-label">利润变化</span>
          <span :class="['metric-value', getMetricClass(profitLift)]">
            {{ profitLift > 0 ? '+' : '' }}{{ profitLift.toFixed(2) }}pt
          </span>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="result-actions">
        <el-button type="success" size="default" @click="handlePublish" v-if="progressPercentage >= 100">
          ✅ 保存结果
        </el-button>
        <el-button type="danger" size="default" @click="handleStop">
          ⛔ 终止测试
        </el-button>
      </div>
    </el-card>

    <!-- 第 3 部分：历史测试记录 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <h3>📜 历史测试记录</h3>
          <el-button type="text" @click="toggleHistoryExpand">
            {{ historyExpanded ? '收起' : '展开' }}
          </el-button>
        </div>
      </template>

      <el-collapse v-model="activeHistory" v-if="historyExpanded">
        <el-collapse-item 
          v-for="(test, index) in abTestHistory" 
          :key="test.id" 
          :name="index.toString()"
        >
          <template #title>
            <div class="history-item-title">
              <span :class="['status-dot', test.status]"></span>
              <span>{{ test.date }} {{ test.name }}（已完成，{{ test.status === 'success' ? '✅ 成功' : '❌ 失败' }}）</span>
            </div>
          </template>
          <div class="history-details">
            <p><strong>适用机构：</strong>{{ test.institutions.join('、') }}</p>
            <p><strong>业务单元：</strong>{{ test.business_units.join('、') }}</p>
            <p><strong>实验结果：</strong>{{ test.result }}</p>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllStrategies, recordTestResult } from '../api/strategy'
// 公共策略加载工具函数
import { loadStrategiesForUI } from '../utils/strategy-transform'

const router = useRouter()

// 已保存的策略列表（从 sessionStorage 加载，与模拟测试使用同一数据源）
const savedStrategies = ref([])

// 实验配置
const experiment = reactive({
  name: '',
  hypothesis: '',
  control_strategy: '',
  treatment_strategy: '',
  traffic_split: 50,
  duration_days: 14,
  institutions: [],
  business_units: [],
  description: ''
})

// 加载策略列表（与模拟测试一致）
onMounted(() => {
  loadStrategies()
})

// 从后端 API 加载策略列表（使用公共工具函数）
const loadStrategies = async () => {
  try {
    // 使用公共工具函数加载并转换策略数据
    savedStrategies.value = await loadStrategiesForUI({
      onError: (error) => {
        ElMessage.error('加载策略失败：' + error.message)
      }
    })
  } catch (error) {
    // 错误已在工具函数中处理
    console.error('加载策略失败:', error)
  }
}

// 影响范围说明
const impactDescription = computed(() => {
  const instCount = experiment.institutions.length
  const buCount = experiment.business_units.length
  if (instCount === 0 && buCount === 0) {
    return '请选择适用机构和业务单元'
  }
  return `本次实验将影响 ${instCount} 个机构，${buCount} 个业务单元的业务`
})

// 实验状态
const starting = ref(false)
const experimentRunning = ref(false)
const progressPercentage = ref(0)
const currentDay = ref(0)
const isSignificant = ref(false)
const pValue = ref('0.023')

// 指标提升（合理的演示数据：基准成交率 50%，绝对值提升 3-5%，利润变化<2pt）
const baseConversionRate = ref(50.0) // 基准成交率 50%
const conversionLift = ref(3.5) // 成交率绝对值提升 3-5%
const profitLift = ref(1.2) // 利润变化不超过 2 个百分点

// 历史展开状态
const historyExpanded = ref(true)
const activeHistory = ref([])

// 问题 7：历史测试记录（使用更具体的命名 abTestHistory）
const abTestHistory = ref([
  {
    id: 'test_001',
    date: '2026-03-15',
    name: '新能源策略测试',
    status: 'success',
    institutions: ['上海', '北京'],
    business_units: ['新能源 - 高价值', '新能源 - 普通'],
    result: '成交率 +12.3%，利润 +8.5%，p=0.018'
  },
  {
    id: 'test_002',
    date: '2026-03-01',
    name: '豪车策略测试',
    status: 'failed',
    institutions: ['上海'],
    business_units: ['豪车 - 续保'],
    result: '成交率 +5.2%，利润 -3.8%，p=0.234（不显著）'
  }
])

// 运行状态
const runningStatus = computed(() => {
  if (progressPercentage.value >= 100) {
    return { type: 'success', icon: '✅', text: '已完成' }
  }
  return { type: '', icon: '🟢', text: '进行中' }
})

// 方法
// 问题 6：A/B 测试启动处理函数
const handleStartTest = async () => {
  // 验证实验基本信息
  if (!experiment.name || !experiment.hypothesis) {
    ElMessage.warning('请填写实验名称和假设')
    return
  }
  if (!experiment.control_strategy) {
    ElMessage.warning('请选择对照组基准')
    return
  }
  if (!experiment.treatment_strategy) {
    ElMessage.warning('请选择实验组策略')
    return
  }
  if (experiment.institutions.length === 0 || experiment.business_units.length === 0) {
    ElMessage.warning('请选择适用机构和业务单元')
    return
  }

  starting.value = true
  
  try {
    // 模拟创建实验
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    experimentRunning.value = true
    progressPercentage.value = 0
    currentDay.value = 0
    
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (progressPercentage.value < 100) {
        progressPercentage.value += 1
        currentDay.value = Math.round(progressPercentage.value * experiment.duration_days / 100)
        
        // 模拟指标更新（合理范围：成交率提升 3-5%，利润变化<2pt）
        conversionLift.value = 3.5 + Math.random() * 2 - 1 // 2.5% ~ 4.5%
        profitLift.value = 1.2 + Math.random() * 0.8 - 0.4 // 0.8pt ~ 1.6pt
        
        if (progressPercentage.value > 50) {
          isSignificant.value = true
          pValue.value = (0.02 + Math.random() * 0.01).toFixed(3)
        }
      } else {
        clearInterval(progressInterval)
        ElMessage.success('实验已完成！')
      }
    }, 200) // 加速演示

    ElMessage.success('A/B 测试已启动！')
  } catch (error) {
    ElMessage.error('启动失败：' + error.message)
  } finally {
    starting.value = false
  }
}

const handleStop = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要终止测试吗？终止后无法恢复数据。',
      '终止测试',
      {
        confirmButtonText: '确定终止',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    experimentRunning.value = false
    ElMessage.success('测试已终止')
  } catch {
    // 用户取消
  }
}

const handlePublish = async () => {
  try {
    // 调用后端 API 记录测试结果并更新策略状态
    if (experiment.treatment_strategy) {
      await recordTestResult(experiment.treatment_strategy, {
        test_type: 'ab_test',
        passed: profitLift.value > 0,
        result_summary: `成交率 ${conversionLift.value > 0 ? '+' : ''}${conversionLift.value.toFixed(2)}%，利润 ${profitLift.value > 0 ? '+' : ''}${profitLift.value.toFixed(2)}pt`,
        conversion_rate_lift: conversionLift.value,
        profit_lift: profitLift.value,
        p_value: parseFloat(pValue.value)
      })
    }
    
    // 同时更新本地历史记录（用于显示）
    const newTest = {
      id: `test_${Date.now()}`,
      date: new Date().toISOString().split('T')[0],
      name: experiment.name,
      status: profitLift.value > 0 ? 'success' : 'failed',
      institutions: [...experiment.institutions],
      business_units: [...experiment.business_units],
      result: `成交率 ${conversionLift.value > 0 ? '+' : ''}${conversionLift.value.toFixed(2)}%，利润 ${profitLift.value > 0 ? '+' : ''}${profitLift.value.toFixed(2)}pt，p=${pValue.value}`
    }
    
    // 问题 7：使用优化后的变量名 abTestHistory
    abTestHistory.value.unshift(newTest)
    
    ElMessage.success('测试结果已保存！')
    
    // 关闭实验结果卡片
    experimentRunning.value = false
  } catch (error) {
    console.error('保存测试结果失败:', error)
    ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
  }
}

const toggleHistoryExpand = () => {
  historyExpanded.value = !historyExpanded.value
  if (historyExpanded.value) {
    activeHistory.value = ['1', '2']
  } else {
    activeHistory.value = []
  }
}

const getMetricClass = (value) => {
  if (value > 10) return 'metric-positive-high'
  if (value > 0) return 'metric-positive'
  if (value < -10) return 'metric-negative-high'
  return 'metric-negative'
}
</script>

<style scoped>
.ab-test-page {
  padding: 24px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-header p {
  color: #909399;
  margin: 0;
  font-size: 13px;
}

.setup-card, .result-card, .history-card {
  max-width: 1000px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.traffic-split-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.traffic-labels {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.control-label {
  color: #909399;
}

.treatment-label {
  color: #409EFF;
  font-weight: 600;
}

.unit-text {
  margin-left: 8px;
  color: #909399;
}

.form-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* 实验结果 */
.progress-section {
  margin: 20px 0;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.significance-badge {
  font-size: 12px;
  color: #67c23a;
  font-weight: 600;
}

.metrics-summary {
  display: flex;
  gap: 32px;
  padding: 20px 0;
  margin-bottom: 20px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-label {
  font-size: 12px;
  color: #909399;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
}

.metric-positive-high {
  color: #67c23a;
}

.metric-positive {
  color: #67c23a;
}

.metric-negative-high {
  color: #f56c6c;
}

.metric-negative {
  color: #f56c6c;
}

.result-actions {
  display: flex;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* 历史记录 */
.history-item-title {
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.success {
  background-color: #67c23a;
}

.status-dot.failed {
  background-color: #f56c6c;
}

.history-details {
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 4px;
}

.history-details p {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
}

:deep(.el-collapse-item__header) {
  font-weight: 500;
}

:deep(.el-collapse-item__content) {
  padding: 0;
}
</style>
