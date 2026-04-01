<template>
  <div class="strategy-detail-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        <h1>策略详情</h1>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="editStrategy">编辑</el-button>
        <el-button type="success" v-if="strategy?.status === 'draft'" @click="publishStrategy">发布</el-button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 详情内容 -->
    <template v-else-if="strategy">
      <!-- 基本信息卡片 -->
      <el-card class="detail-card mb-4">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>基本信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="策略名称">{{ strategy.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(strategy.status)">
              {{ getStatusLabel(strategy.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="生效机构">
            <span v-if="strategy?.institutions?.length">
              {{ strategy.institutions.map(i => i.name || i).join('、') }}
            </span>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="业务单元数">
            {{ strategy?.business_units?.length || strategy?.business_units_count || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="版本号">v{{ strategy?.version }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(strategy?.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">{{ formatDate(strategy?.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="策略描述" :span="2">
            {{ strategy?.description || '无' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 业务单元配置 -->
      <el-card class="detail-card mb-4" v-if="strategy?.business_units?.length">
        <template #header>
          <div class="card-header">
            <el-icon><DataBoard /></el-icon>
            <span>业务单元配置</span>
          </div>
        </template>
        <el-table :data="strategy?.business_units || []" stripe>
          <el-table-column prop="unit_id" label="业务单元 ID" width="120" />
          <el-table-column prop="unit_name" label="业务单元名称" min-width="180" />
          <el-table-column prop="policies" label="保单数" width="100" align="right">
            <template #default="{ row }">{{ row.policies?.toLocaleString() || '-' }}</template>
          </el-table-column>
          <el-table-column prop="avg_premium" label="平均保费" width="120" align="right">
            <template #default="{ row }">¥{{ (row.avg_premium || 0).toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="expected_profit_margin" label="预期利润率" width="100" align="center">
            <template #default="{ row }">
              <span class="margin-badge" :class="getMarginClass(row.expected_profit_margin)">
                {{ ((row.expected_profit_margin || 0) * 100).toFixed(1) }}%
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 成本模拟配置 -->
      <el-card class="detail-card mb-4" v-if="strategy?.cost_simulation">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            <span>成本模拟配置</span>
          </div>
        </template>
        
        <h4>全局参数</h4>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="固定成本率">
            {{ (((strategy?.cost_simulation?.global_params?.fixed_cost_ratio) || 0) * 100).toFixed(1) }}%
          </el-descriptions-item>
          <el-descriptions-item label="目标赔付率">
            {{ (((strategy?.cost_simulation?.global_params?.target_loss_ratio) || 0) * 100).toFixed(1) }}%
          </el-descriptions-item>
          <el-descriptions-item label="市场费用率">
            {{ (((strategy?.cost_simulation?.global_params?.market_expense_ratio) || 0) * 100).toFixed(1) }}%
          </el-descriptions-item>
          <el-descriptions-item label="自主系数区间">
            {{ (strategy?.cost_simulation?.global_params?.autonomous_discount_min)?.toFixed(2) || '-' }} ~ {{ (strategy?.cost_simulation?.global_params?.autonomous_discount_max)?.toFixed(2) || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="反算折扣">
            {{ strategy?.cost_simulation?.global_params?.is_calculate ? '是' : '否' }}
          </el-descriptions-item>
        </el-descriptions>

        <h4 v-if="strategy?.cost_simulation?.business_unit_params?.length">业务单元成本参数</h4>
        <el-table 
          v-if="strategy?.cost_simulation?.business_unit_params?.length" 
          :data="strategy?.cost_simulation?.business_unit_params || []" 
          stripe 
          size="small"
          class="mt-3"
        >
          <el-table-column prop="unit_name" label="业务单元" min-width="150" />
          <el-table-column prop="policies" label="保单数" width="90" align="right">
            <template #default="{ row }">{{ row.policies?.toLocaleString() || '-' }}</template>
          </el-table-column>
          <el-table-column prop="avg_premium" label="平均保费" width="100" align="right">
            <template #default="{ row }">¥{{ (row.avg_premium || 0).toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="pure_risk_cost" label="纯风险成本" width="100" align="right">
            <template #default="{ row }">¥{{ ((row.pure_risk_cost || 0) / 10000).toFixed(0) }}万</template>
          </el-table-column>
          <el-table-column prop="autonomous_discount_min" label="自主系数下限" width="100" align="center">
            <template #default="{ row }">{{ (row.autonomous_discount_min || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="autonomous_discount_max" label="自主系数上限" width="100" align="center">
            <template #default="{ row }">{{ (row.autonomous_discount_max || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="fixed_cost_ratio" label="固定成本率" width="90" align="center">
            <template #default="{ row }">{{ ((row.fixed_cost_ratio || 0) * 100).toFixed(1) }}%</template>
          </el-table-column>
          <el-table-column prop="target_loss_ratio" label="目标赔付率" width="90" align="center">
            <template #default="{ row }">{{ ((row.target_loss_ratio || 0) * 100).toFixed(1) }}%</template>
          </el-table-column>
          <el-table-column prop="market_expense_ratio" label="市场费用率" width="90" align="center">
            <template #default="{ row }">{{ ((row.market_expense_ratio || 0) * 100).toFixed(1) }}%</template>
          </el-table-column>
          <el-table-column prop="expected_profit_margin" label="预期利润率" width="90" align="center">
            <template #default="{ row }">
              <span :class="getMarginClass(row.expected_profit_margin)">
                {{ ((row.expected_profit_margin || 0) * 100).toFixed(1) }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="is_calculate" label="反算折扣" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_calculate ? 'success' : 'info'" size="small">
                {{ row.is_calculate ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 操作历史 -->
      <el-card class="detail-card">
        <template #header>
          <div class="card-header">
            <el-icon><Clock /></el-icon>
            <span>操作历史</span>
          </div>
        </template>
        <el-timeline v-if="timeline?.length">
          <el-timeline-item
            v-for="(item, index) in timeline"
            :key="index"
            :timestamp="item.timestamp"
            placement="top"
            :type="item.type"
          >
            <el-card>
              <h4>{{ item.title }}</h4>
              <p>{{ item.description }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </template>

    <!-- 无数据 -->
    <el-empty v-else description="未找到策略信息" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, DataBoard, Setting, Clock, ArrowLeft } from '@element-plus/icons-vue'
import { getStrategy, updateStrategyStatus } from '../../api/strategy'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const strategy = ref(null)
const timeline = ref([])

// 加载策略详情
const loadStrategyDetail = async () => {
  loading.value = true
  try {
    const response = await getStrategy(route.params.id)
    if (isUnmounted) return
    strategy.value = response.data || response
    
    // 构建时间线
    timeline.value = [
      {
        title: '策略创建',
        description: `策略 "${strategy.value.name}" 创建`,
        timestamp: formatDate(strategy.value.created_at),
        type: 'success'
      }
    ]
    
    if (strategy.value.updated_at && strategy.value.updated_at !== strategy.value.created_at) {
      if (isUnmounted) return
      timeline.value.push({
        title: '策略更新',
        description: '策略配置已更新',
        timestamp: formatDate(strategy.value.updated_at),
        type: 'primary'
      })
    }
  } catch (error) {
    console.error('加载策略详情失败:', error)
    ElMessage.error('加载失败：' + error.message)
  } finally {
    if (!isUnmounted) {
      loading.value = false
    }
  }
}

// 编辑策略
const editStrategy = () => {
  router.push(`/admin/strategy/edit/${route.params.id}`)
}

// 发布策略
const publishStrategy = async () => {
  try {
    await ElMessageBox.confirm(
      `确认发布策略 "${strategy.value.name}" 吗？发布后将无法编辑。`,
      '确认发布',
      { type: 'warning' }
    )
    
    // TODO: 调用发布 API
    ElMessage.success('策略发布成功')
    loadStrategyDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('发布失败：' + error.message)
    }
  }
}

// 返回
const goBack = () => {
  router.back()
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    draft: '',
    simulation_passed: 'success',
    simulation_failed: 'danger',
    published: 'primary',
    disabled: 'info'
  }
  return types[status] || ''
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labels = {
    draft: '草稿',
    simulation_passed: '模拟通过',
    simulation_failed: '模拟失败',
    published: '已发布',
    disabled: '已禁用'
  }
  return labels[status] || status
}

// 获取利润率样式类
const getMarginClass = (margin) => {
  if (!margin) return ''
  const percent = margin * 100
  if (percent >= 5) return 'margin-high'
  if (percent >= 3) return 'margin-medium'
  return 'margin-low'
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

let isUnmounted = false

onMounted(() => {
  loadStrategyDetail()
})

onBeforeUnmount(() => {
  isUnmounted = true
})
</script>

<style scoped>
.strategy-detail-page {
  padding: 24px;
  min-height: 100vh;
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.detail-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.card-header .el-icon {
  font-size: 18px;
}

.loading-container {
  padding: 20px;
}

h4 {
  margin: 16px 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.margin-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.margin-high {
  background-color: #f0f9ff;
  color: #0284c7;
}

.margin-medium {
  background-color: #fef3c7;
  color: #d97706;
}

.margin-low {
  background-color: #fee2e2;
  color: #dc2626;
}

.mb-4 {
  margin-bottom: 16px;
}

.mt-3 {
  margin-top: 12px;
}
</style>
