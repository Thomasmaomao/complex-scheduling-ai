<template>
  <div class="publish-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>策略发布与效果分析 - 全量发布</h1>
      <p>将已通过测试的策略发布到生产环境</p>
    </div>

    <!-- 第 1 部分：发布策略选择 -->
    <el-card class="strategy-card">
      <template #header>
        <div class="card-header">
          <h3>📋 已通过测试的策略</h3>
        </div>
      </template>

      <div class="strategy-list">
        <div 
          v-for="strategy in availableStrategies" 
          :key="strategy.id"
          :class="['strategy-item', { selected: selectedStrategy?.id === strategy.id }]"
          @click="selectStrategy(strategy)"
        >
          <div class="strategy-checkbox">
            <el-checkbox 
              :model-value="selectedStrategy?.id === strategy.id"
              @click.stop="selectStrategy(strategy)"
            />
          </div>
          <div class="strategy-content">
            <div class="strategy-header">
              <h4>{{ strategy.name }}</h4>
              <el-tag :type="strategy.testType === 'ab' ? 'success' : 'warning'" size="small">
                {{ strategy.testType === 'ab' ? '✅ A/B 测试通过' : '🟡 模拟测试通过' }}
              </el-tag>
            </div>
            <div class="strategy-info">
              <span><strong>适用机构：</strong>{{ strategy.institutions.join('、') }}</span>
              <span><strong>业务单元：</strong>{{ strategy.businessUnits.join('、') }}</span>
            </div>
            <div class="strategy-description">
              <strong>描述：</strong>{{ strategy.description }}
            </div>
          </div>
        </div>

        <div v-if="availableStrategies.length === 0" class="empty-state">
          <el-empty description="暂无已通过测试的策略，请先完成策略测试" />
        </div>
      </div>
    </el-card>

    <!-- 第 2 部分：发布设置 -->
    <el-card v-if="selectedStrategy" class="settings-card">
      <template #header>
        <div class="card-header">
          <h3>⚙️ 发布设置</h3>
        </div>
      </template>

      <el-form :model="publishConfig" label-width="100px" size="default">
        <!-- 第 1 行：发布范围 + 发布时间 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发布范围" required>
              <el-radio-group v-model="publishConfig.scope">
                <el-radio label="all">全量</el-radio>
                <el-radio label="specified">指定机构</el-radio>
                <el-radio label="channel">指定渠道</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发布时间" required>
              <el-radio-group v-model="publishConfig.timing">
                <el-radio label="immediate">立即</el-radio>
                <el-radio label="scheduled">定时</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第 2 行：指定机构 + 定时时间 -->
        <el-row :gutter="20" v-if="publishConfig.scope === 'specified' || publishConfig.timing === 'scheduled'">
          <el-col :span="12" v-if="publishConfig.scope === 'specified'">
            <el-form-item label="指定机构" required>
              <el-checkbox-group v-model="publishConfig.institutions">
                <el-checkbox label="上海" />
                <el-checkbox label="北京" />
                <el-checkbox label="广东" />
                <el-checkbox label="浙江" />
              </el-checkbox-group>
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="publishConfig.timing === 'scheduled'">
            <el-form-item label="定时时间" required>
              <el-date-picker
                v-model="publishConfig.scheduled_time"
                type="datetime"
                placeholder="选择发布时间"
                format="YYYY-MM-DD HH:mm"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第 3 行：业务单元 -->
        <el-form-item label="业务单元" required>
          <el-checkbox-group v-model="publishConfig.business_units">
            <el-checkbox label="燃油车 - 续保" />
            <el-checkbox label="燃油车 - 新保" />
            <el-checkbox label="新能源 - 高价值" />
            <el-checkbox label="新能源 - 普通" />
            <el-checkbox label="豪车 - 续保" />
          </el-checkbox-group>
        </el-form-item>

        <!-- 第 4 行：发布描述 + 回滚预案 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发布描述" required>
              <el-input
                v-model="publishConfig.description"
                type="textarea"
                :rows="4"
                placeholder="请说明发布目的和预期效果"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="回滚预案" required>
              <el-input
                v-model="publishConfig.rollback_plan"
                type="textarea"
                :rows="4"
                placeholder="例如：利润率连续 7 天低于 3.0%，自动回滚"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 回滚提示 -->
        <el-alert
          title="回滚预案已启用：利润率连续 7 天低于 3.0%，系统将自动启动回滚机制至上一版本"
          type="warning"
          :closable="false"
          show-icon
          style="margin: 16px 0"
        />

        <!-- 影响范围说明 -->
        <el-alert
          :title="impactDescription"
          type="info"
          :closable="false"
          show-icon
          style="margin: 16px 0"
        />

        <!-- 底部按钮 -->
        <div class="form-actions">
          <el-button @click="handleReset">取消</el-button>
          <el-button type="success" @click="handlePublish" :loading="publishing">
            {{ publishing ? '发布中...' : '确认发布' }}
          </el-button>
        </div>
      </el-form>
    </el-card>

    <!-- 发布成功 -->
    <el-card v-if="published" class="success-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h3>📦 发布状态</h3>
          <el-tag type="success" size="default">🟢 已发布</el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="策略 ID">
          {{ publishId }}
        </el-descriptions-item>
        <el-descriptions-item label="策略名称">
          {{ selectedStrategy?.name }}
        </el-descriptions-item>
        <el-descriptions-item label="发布时间">
          {{ publishTime }}
        </el-descriptions-item>
        <el-descriptions-item label="发布范围">
          {{ getScopeLabel(publishConfig.scope) }}
        </el-descriptions-item>
        <el-descriptions-item label="适用机构">
          {{ publishConfig.institutions?.length || 0 }} 个
        </el-descriptions-item>
        <el-descriptions-item label="业务单元">
          {{ publishConfig.business_units?.length || 0 }} 个
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag type="success">生效中</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <div class="result-footer">
        <el-button @click="handleViewStrategies">查看已发布策略</el-button>
        <el-button type="primary" @click="handleNext">查看效果看板</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllStrategies, publishStrategy } from '../api/strategy'
// 公共策略加载工具函数
import { loadStrategiesForUI } from '../utils/strategy-transform'

const router = useRouter()

// 可用策略列表（从后端 API 加载）
const availableStrategies = ref([])

// 选中的策略
const selectedStrategy = ref(null)

// 发布配置
const publishConfig = reactive({
  scope: 'specified',
  institutions: ['上海', '北京', '广东', '浙江'],
  business_units: ['燃油车 - 续保', '燃油车 - 新保'],
  timing: 'immediate',
  scheduled_time: null,
  description: '',
  rollback_plan: '利润率连续 7 天低于 3.0%，自动回滚至基准策略'
})

// 影响范围说明
const impactDescription = computed(() => {
  const instCount = publishConfig.institutions.length
  const buCount = publishConfig.business_units.length
  if (instCount === 0 && buCount === 0) {
    return '请选择发布范围和业务单元'
  }
  return `本次发布将影响 ${instCount} 个机构，${buCount} 个业务单元的业务`
})

// 发布状态
const publishing = ref(false)
const published = ref(false)
const publishId = ref('')
const publishTime = ref('')

// 问题 6：方法定义
// 选择策略处理函数
const selectStrategy = (strategy) => {
  if (selectedStrategy.value?.id === strategy.id) {
    selectedStrategy.value = null
  } else {
    selectedStrategy.value = strategy
    // 问题 6：自动填充业务单元和机构（处理下划线和驼峰两种格式）
    publishConfig.business_units = [...(strategy.businessUnits || strategy.business_units || [])]
    publishConfig.institutions = [...(strategy.institutions || [])]
  }
}

// 加载已通过测试的策略（与 A/B 测试、模拟测试数据打通）
const loadTestedStrategies = async () => {
  try {
    // 使用公共工具函数加载并转换策略数据
    const strategiesData = await loadStrategiesForUI({
      onError: (error) => {
        ElMessage.error('加载策略失败：' + error.message)
      }
    })
    
    // 所有状态的策略都显示（不过滤）
    availableStrategies.value = strategiesData.map(strategy => ({
      id: strategy.id,
      name: strategy.name,
      description: strategy.description,
      testType: strategy.status.includes('ab_test') ? 'ab' : strategy.status.includes('simulation') ? 'simulation' : 'other',
      institutions: strategy.institutions,
      businessUnits: strategy.businessUnits,
      status: strategy.status
    }))
  } catch (error) {
    // 错误已在工具函数中处理
    console.error('加载策略失败:', error)
  }
}

// 组件挂载时加载策略
onMounted(() => {
  loadTestedStrategies()
})

const handleReset = () => {
  selectedStrategy.value = null
  publishConfig.scope = 'specified'
  publishConfig.institutions = []
  publishConfig.business_units = []
  publishConfig.timing = 'immediate'
  publishConfig.scheduled_time = null
  publishConfig.description = ''
  publishConfig.rollback_plan = '利润率连续 7 天低于 3.0%，自动回滚至基准策略'
  published.value = false
  ElMessage.info('已重置配置')
}

const handlePublish = async () => {
  // 验证
  if (!selectedStrategy.value) {
    ElMessage.warning('请选择要发布的策略')
    return
  }
  if (publishConfig.institutions.length === 0) {
    ElMessage.warning('请选择发布机构')
    return
  }
  if (publishConfig.business_units.length === 0) {
    ElMessage.warning('请选择业务单元')
    return
  }
  if (!publishConfig.description) {
    ElMessage.warning('请填写发布描述')
    return
  }
  if (!publishConfig.rollback_plan) {
    ElMessage.warning('请填写回滚预案')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认发布"${selectedStrategy.value.name}"到生产环境？发布后将影响真实用户询价。`,
      '全量发布确认',
      {
        confirmButtonText: '确认发布',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    publishing.value = true
    
    // 调用后端 API 发布策略
    const publishData = {
      publish_scope: publishConfig.scope,
      publish_description: publishConfig.description,
      rollback_plan: publishConfig.rollback_plan,
      timing_type: publishConfig.timing,
      scheduled_time: publishConfig.scheduled_time,
      institutions: publishConfig.institutions.map(name => ({ code: name.toLowerCase(), name })),
      business_units: publishConfig.business_units.map(name => ({ id: name, name }))
    }
    
    const response = await publishStrategy(selectedStrategy.value.id, publishData)
    
    // publishStrategy 已经返回 response.data（对象）
    publishId.value = response.publish_id
    publishTime.value = new Date().toLocaleString('zh-CN')
    published.value = true

    ElMessage.success('策略已成功发布到生产环境')
  } catch (error) {
    // ElementPlus 取消时 error.name 为 'Cancel'
    if (error.name !== 'Cancel' && error !== 'cancel') {
      ElMessage.error('发布失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    publishing.value = false
  }
}

const handleViewStrategies = () => {
  ElMessage.info('查看已发布策略功能开发中')
}

const handleNext = () => {
  ElMessage.success('跳转到效果看板')
  router.push('/admin/effect-dashboard')
}

const getScopeLabel = (scope) => {
  const labels = {
    'specified': '指定机构',
    'all': '全量',
    'channel': '指定渠道'
  }
  return labels[scope] || scope
}

</script>

<style scoped>
.publish-page {
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

.strategy-card, .settings-card, .success-card {
  width: 100%;
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

.strategy-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.strategy-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.strategy-item:hover {
  border-color: #67c23a;
  background-color: #f0f9ff;
}

.strategy-item.selected {
  border-color: #67c23a;
  background-color: #f0f9ff;
}

.strategy-checkbox {
  display: flex;
  align-items: flex-start;
}

.strategy-content {
  flex: 1;
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.strategy-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.strategy-info {
  display: flex;
  gap: 24px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.strategy-description {
  font-size: 13px;
  color: #909399;
}

.empty-state {
  padding: 40px 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.result-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

:deep(.el-checkbox-group .el-checkbox) {
  margin-right: 0;
  margin-bottom: 8px;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}
</style>
