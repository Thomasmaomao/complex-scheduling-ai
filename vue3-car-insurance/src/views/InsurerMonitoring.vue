<template>
  <div class="insurer-monitoring-page">
    <div class="page-header">
      <h1>📈 保司动态监控</h1>
      <p>实时监控保司额度和赔付率，手动干预优先级</p>
    </div>

    <!-- 监控概览 -->
    <el-row :gutter="20" class="metric-cards">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">监控保司数</div>
          <div class="metric-value">{{ insurerList.length }}</div>
          <div class="metric-sub">家保司</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">额度预警</div>
          <div class="metric-value warning">{{ warningCount.quota }}</div>
          <div class="metric-sub">家保司额度紧张</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">赔付率预警</div>
          <div class="metric-value danger">{{ warningCount.loss_ratio }}</div>
          <div class="metric-sub">家保司赔付率过高</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-label">今日调整</div>
          <div class="metric-value">{{ todayAdjustments }}</div>
          <div class="metric-sub">次优先级调整</div>
        </div>
      </el-col>
    </el-row>

    <!-- 保司监控列表 -->
    <el-card class="monitoring-card">
      <template #header>
        <div class="card-header">
          <h3>保司实时监控</h3>
          <el-button type="primary" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="insurerList" stripe style="width: 100%">
        <el-table-column prop="insurer_name" label="保司名称" min-width="150" />
        
        <!-- 额度监控 -->
        <el-table-column label="保费额度监控" width="250">
          <template #default="{ row }">
            <div class="quota-progress">
              <el-progress 
                :percentage="row.quota_usage_rate * 100" 
                :color="getQuotaColor(row.quota_usage_rate)"
                :format="formatQuota"
              />
            </div>
            <div class="quota-detail">
              <span>已用 ¥{{ (row.used_quota / 10000).toFixed(0) }}万</span>
              <span>/</span>
              <span>目标 ¥{{ (row.target_quota / 10000).toFixed(0) }}万</span>
            </div>
          </template>
        </el-table-column>

        <!-- 赔付率监控 -->
        <el-table-column label="赔付率监控" width="250">
          <template #default="{ row }">
            <div class="loss-ratio-display">
              <div class="loss-ratio-value" :class="getLossRatioClass(row.actual_loss_ratio)">
                {{ (row.actual_loss_ratio * 100).toFixed(1) }}%
              </div>
              <div class="loss-ratio-target">
                目标：{{ (row.target_loss_ratio * 100).toFixed(0) }}%
                <span :class="getDeviationClass(row.loss_ratio_deviation)">
                  (偏差 {{ row.loss_ratio_deviation >= 0 ? '+' : '' }}{{ (row.loss_ratio_deviation * 100).toFixed(1) }}%)
                </span>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 优先级 -->
        <el-table-column label="优先级" width="200">
          <template #default="{ row }">
            <div class="priority-display">
              <div class="priority-base">基础：{{ row.base_priority }}</div>
              <div class="priority-adjustment">
                调整：
                <span :class="row.quota_adjustment >= 0 ? 'adjustment-positive' : 'adjustment-negative'">
                  {{ row.quota_adjustment >= 0 ? '+' : '' }}{{ row.quota_adjustment }}%
                </span>
                <span :class="row.loss_ratio_adjustment >= 0 ? 'adjustment-positive' : 'adjustment-negative'">
                  {{ row.loss_ratio_adjustment >= 0 ? '+' : '' }}{{ row.loss_ratio_adjustment }}%
                </span>
              </div>
              <div class="priority-final">
                最终：<el-tag :type="getPriorityType(row.final_priority)" size="large">{{ row.final_priority }}</el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 状态 -->
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 操作 -->
        <el-table-column label="手动干预" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleAdjust(row)">
              调整优先级
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 调整记录 -->
    <el-card class="history-card">
      <template #header>
        <h3>近期调整记录</h3>
      </template>

      <el-table :data="adjustmentHistory" stripe style="width: 100%">
        <el-table-column prop="insurer_name" label="保司名称" width="150" />
        <el-table-column prop="adjustment_date" label="调整时间" width="180" />
        <el-table-column prop="adjustment_type" label="调整类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.adjustment_type === '自动' ? 'info' : 'warning'">
              {{ row.adjustment_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="调整原因" />
        <el-table-column prop="priority_change" label="优先级变化" width="120">
          <template #default="{ row }">
            <span :class="row.priority_change >= 0 ? 'adjustment-positive' : 'adjustment-negative'">
              {{ row.priority_change >= 0 ? '+' : '' }}{{ row.priority_change }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElDialog } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

// 保司监控列表
const insurerList = ref([
  {
    insurer_id: 'picc',
    insurer_name: '人保财险',
    target_quota: 10000000,
    used_quota: 4000000,
    quota_usage_rate: 0.40,
    target_loss_ratio: 0.75,
    actual_loss_ratio: 0.70,
    loss_ratio_deviation: -0.05,
    base_priority: 80,
    quota_adjustment: 20,
    loss_ratio_adjustment: 5,
    final_priority: 100,
    status: 'normal'
  },
  {
    insurer_id: 'pingan',
    insurer_name: '平安产险',
    target_quota: 8000000,
    used_quota: 6400000,
    quota_usage_rate: 0.80,
    target_loss_ratio: 0.75,
    actual_loss_ratio: 0.78,
    loss_ratio_deviation: 0.03,
    base_priority: 75,
    quota_adjustment: -20,
    loss_ratio_adjustment: 0,
    final_priority: 60,
    status: 'warning'
  },
  {
    insurer_id: 'cpic',
    insurer_name: '太平洋产险',
    target_quota: 12000000,
    used_quota: 13200000,
    quota_usage_rate: 1.10,
    target_loss_ratio: 0.75,
    actual_loss_ratio: 0.92,
    loss_ratio_deviation: 0.17,
    base_priority: 85,
    quota_adjustment: -50,
    loss_ratio_adjustment: -15,
    final_priority: 30,
    status: 'danger'
  }
])

// 调整记录
const adjustmentHistory = ref([
  {
    insurer_name: '人保财险',
    adjustment_date: '2026-03-30 10:00:00',
    adjustment_type: '自动',
    reason: '额度使用率<50%，赔付率低于目标',
    priority_change: 25
  },
  {
    insurer_name: '太平洋产险',
    adjustment_date: '2026-03-30 09:30:00',
    adjustment_type: '自动',
    reason: '额度使用率>100%，赔付率严重超标',
    priority_change: -65
  }
])

// 预警统计
const warningCount = computed(() => {
  return {
    quota: insurerList.value.filter(i => i.quota_usage_rate > 0.8).length,
    loss_ratio: insurerList.value.filter(i => i.loss_ratio_deviation > 0.1).length
  }
})

// 今日调整次数
const todayAdjustments = ref(5)

// 方法
const handleRefresh = () => {
  // TODO: 调用后端 API 刷新数据
  ElMessage.success('数据已刷新')
}

const handleAdjust = (row) => {
  ElMessage.info(`调整 ${row.insurer_name} 优先级`)
  // TODO: 打开调整对话框
}

const getQuotaColor = (rate) => {
  if (rate < 0.5) return '#67c23a'
  if (rate < 0.8) return '#409eff'
  if (rate < 1.0) return '#e6a23c'
  return '#f56c6c'
}

const formatQuota = (percentage) => {
  return `${percentage.toFixed(0)}%`
}

const getLossRatioClass = (ratio) => {
  if (ratio < 0.7) return 'loss-low'
  if (ratio < 0.85) return 'loss-normal'
  return 'loss-high'
}

const getDeviationClass = (deviation) => {
  if (deviation > 0.1) return 'deviation-danger'
  if (deviation > 0.05) return 'deviation-warning'
  if (deviation < -0.1) return 'deviation-low'
  return ''
}

const getPriorityType = (priority) => {
  if (priority >= 80) return 'success'
  if (priority >= 50) return 'primary'
  if (priority >= 30) return 'warning'
  return 'danger'
}

const getStatusType = (status) => {
  const types = {
    'normal': 'success',
    'warning': 'warning',
    'danger': 'danger'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    'normal': '正常',
    'warning': '预警',
    'danger': '危险'
  }
  return labels[status] || status
}

const adjustmentPositive = 'adjustment-positive'
const adjustmentNegative = 'adjustment-negative'
</script>

<style scoped>
.insurer-monitoring-page {
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

.metric-cards {
  margin-bottom: 20px;
}

.metric-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 8px;
  text-align: center;
}

.metric-card.warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.metric-card.danger {
  background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
}

.metric-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.metric-sub {
  font-size: 12px;
  opacity: 0.8;
}

.monitoring-card, .history-card {
  margin-bottom: 20px;
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

.quota-progress {
  margin-bottom: 8px;
}

.quota-detail {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 4px;
}

.loss-ratio-display {
  text-align: center;
}

.loss-ratio-value {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.loss-low {
  color: #67c23a;
}

.loss-normal {
  color: #409eff;
}

.loss-high {
  color: #f56c6c;
}

.loss-ratio-target {
  font-size: 12px;
  color: #909399;
}

.deviation-danger {
  color: #f56c6c;
  font-weight: 600;
}

.deviation-warning {
  color: #e6a23c;
  font-weight: 600;
}

.deviation-low {
  color: #67c23a;
  font-weight: 600;
}

.priority-display {
  text-align: center;
}

.priority-base {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.priority-adjustment {
  font-size: 12px;
  margin-bottom: 4px;
}

.priority-final {
  margin-top: 4px;
}

.adjustment-positive {
  color: #67c23a;
  font-weight: 600;
}

.adjustment-negative {
  color: #f56c6c;
  font-weight: 600;
}
</style>
