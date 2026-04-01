<template>
  <div class="insurer-intervention-page">
    <div class="page-header">
      <h1>📊 保司配置中心 - 动态干预</h1>
      <p>监控保司实时状态，手动干预优先级，调整立即生效到用户询价推荐</p>
    </div>

    <!-- 第 1 部分：保司优先级实时状态 -->
    <el-row :gutter="20" class="status-cards">
      <el-col :span="8" v-for="insurer in insurers" :key="insurer.id">
        <div class="status-card" :class="'status-' + insurer.priority_level">
          <div class="card-header">
            <h3>{{ insurer.name }}</h3>
            <el-tag v-if="insurer.priority_level === 'high'" type="success" size="small">🟢 优先推荐</el-tag>
            <el-tag v-else-if="insurer.priority_level === 'normal'" type="warning" size="small">🟡 正常推荐</el-tag>
            <el-tag v-else type="danger" size="small">🔴 限制推荐</el-tag>
          </div>
          <div class="card-content">
            <div class="metric-row">
              <span class="metric-label">基础优先级</span>
              <span class="metric-value">{{ insurer.base_priority }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">当前优先级</span>
              <span class="metric-value highlight">{{ insurer.current_priority }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">调整幅度</span>
              <span class="metric-value" :class="insurer.adjustment >= 0 ? 'positive' : 'negative'">
                {{ insurer.adjustment >= 0 ? '+' : '' }}{{ insurer.adjustment }}%
              </span>
            </div>
          </div>
          <div class="card-actions">
            <el-button type="primary" size="small" @click="showAdjustDialog(insurer)">手动调整</el-button>
            <el-button size="small" @click="showDetail(insurer)">查看明细</el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 第 2 部分：额度使用监控 -->
    <el-card class="monitor-card">
      <template #header>
        <h3>额度使用监控</h3>
      </template>
      <div class="quota-monitor">
        <div v-for="insurer in insurers" :key="'quota-'+insurer.id" class="quota-item">
          <div class="quota-header">
            <span class="insurer-name">{{ insurer.name }}</span>
            <span class="quota-info">
              目标 ¥{{ insurer.quota_target }}万 | 
              已用 ¥{{ insurer.quota_used }}万 | 
              使用率 <strong :class="getUsageClass(insurer.quota_usage)">{{ insurer.quota_usage }}%</strong>
              <span v-if="insurer.quota_usage > 100" class="warning-icon">⚠️</span>
            </span>
            <span class="adjustment-badge" :class="getAdjustmentClass(insurer.quota_adjustment)">
              {{ insurer.quota_adjustment >= 0 ? '+' : '' }}{{ insurer.quota_adjustment }}%
            </span>
          </div>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :class="getUsageClass(insurer.quota_usage)"
              :style="{ width: Math.min(insurer.quota_usage, 100) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 第 3 部分：赔付率监控 -->
    <el-card class="monitor-card">
      <template #header>
        <h3>赔付率监控</h3>
      </template>
      <div class="loss-ratio-monitor">
        <div v-for="insurer in insurers" :key="'loss-'+insurer.id" class="loss-item">
          <div class="loss-header">
            <span class="insurer-name">{{ insurer.name }}</span>
            <span class="loss-info">
              目标 {{ insurer.loss_ratio_target }}% | 
              实际 <strong :class="getLossClass(insurer.loss_ratio_actual)">{{ insurer.loss_ratio_actual }}%</strong> | 
              偏差 <span :class="insurer.loss_ratio_deviation >= 0 ? 'positive' : 'negative'">
                {{ insurer.loss_ratio_deviation >= 0 ? '+' : '' }}{{ insurer.loss_ratio_deviation }}%
              </span>
              <span v-if="insurer.loss_ratio_actual > insurer.loss_ratio_target + 10" class="warning-icon">⚠️</span>
            </span>
            <span class="adjustment-badge" :class="getAdjustmentClass(insurer.loss_adjustment)">
              {{ insurer.loss_adjustment >= 0 ? '+' : '' }}{{ insurer.loss_adjustment }}%
            </span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 第 4 部分：干预记录 -->
    <el-card class="record-card">
      <template #header>
        <div class="card-header">
          <h3>干预记录（最近 10 条）</h3>
          <el-button type="primary" size="small" @click="exportRecords">
            <el-icon><Download /></el-icon>
            导出干预记录
          </el-button>
        </div>
      </template>
      <el-table :data="interventionRecords" stripe style="width: 100%">
        <el-table-column prop="time" label="时间" width="160" />
        <el-table-column prop="insurer" label="保司" width="100" />
        <el-table-column prop="type" label="调整类型" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="row.type === '临时' ? 'warning' : 'success'">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="adjustment" label="调整幅度" width="100" align="right">
          <template #default="{ row }">
            <span :class="row.adjustment >= 0 ? 'positive' : 'negative'">
              {{ row.adjustment >= 0 ? '+' : '' }}{{ row.adjustment }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="priority_after" label="调整后" width="80" align="right" />
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column prop="scope" label="影响范围" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 保司数据
const insurers = reactive([
  {
    id: 1,
    name: '保司 A',
    base_priority: 80,
    current_priority: 100,
    priority_level: 'high',
    adjustment: 25,
    quota_target: 1000,
    quota_used: 400,
    quota_usage: 40,
    quota_adjustment: 20,
    loss_ratio_target: 75,
    loss_ratio_actual: 70,
    loss_ratio_deviation: -5,
    loss_adjustment: 5
  },
  {
    id: 2,
    name: '保司 B',
    base_priority: 75,
    current_priority: 75,
    priority_level: 'normal',
    adjustment: 0,
    quota_target: 800,
    quota_used: 640,
    quota_usage: 80,
    quota_adjustment: 0,
    loss_ratio_target: 75,
    loss_ratio_actual: 78,
    loss_ratio_deviation: 3,
    loss_adjustment: 0
  },
  {
    id: 3,
    name: '保司 C',
    base_priority: 85,
    current_priority: 30,
    priority_level: 'low',
    adjustment: -65,
    quota_target: 1200,
    quota_used: 1320,
    quota_usage: 110,
    quota_adjustment: -50,
    loss_ratio_target: 75,
    loss_ratio_actual: 92,
    loss_ratio_deviation: 17,
    loss_adjustment: -15
  }
])

// 干预记录
const interventionRecords = reactive([
  { time: '03-29 10:00', insurer: '保司 C', type: '临时', adjustment: -30, priority_after: 30, operator: '张三', scope: '4 机构' },
  { time: '03-28 15:30', insurer: '保司 A', type: '永久', adjustment: 10, priority_after: 100, operator: '李四', scope: '4 机构' },
  { time: '03-27 09:15', insurer: '保司 B', type: '临时', adjustment: -10, priority_after: 65, operator: '王五', scope: '2 机构' },
  { time: '03-26 14:20', insurer: '保司 C', type: '永久', adjustment: -20, priority_after: 65, operator: '张三', scope: '4 机构' },
  { time: '03-25 11:00', insurer: '保司 A', type: '临时', adjustment: 5, priority_after: 95, operator: '李四', scope: '1 机构' }
])

// 获取使用率颜色类
const getUsageClass = (usage) => {
  if (usage > 100) return 'usage-red'
  if (usage > 80) return 'usage-orange'
  if (usage > 50) return 'usage-yellow'
  return 'usage-green'
}

// 获取赔付率颜色类
const getLossClass = (loss) => {
  if (loss > 90) return 'loss-red'
  if (loss > 80) return 'loss-orange'
  if (loss > 75) return 'loss-yellow'
  return 'loss-green'
}

// 获取调整幅度颜色类
const getAdjustmentClass = (adjustment) => {
  if (adjustment > 0) return 'adjust-positive'
  if (adjustment < 0) return 'adjust-negative'
  return 'adjust-neutral'
}

// 显示调整对话框
const showAdjustDialog = (insurer) => {
  ElMessage.info(`手动调整 ${insurer.name} 优先级功能开发中...`)
}

// 显示明细
const showDetail = (insurer) => {
  ElMessage.info(`查看 ${insurer.name} 明细功能开发中...`)
}

// 导出记录
const exportRecords = () => {
  ElMessage.success('干预记录已导出')
}
</script>

<style scoped>
.insurer-intervention-page {
  padding: 24px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
}

.page-header p {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

/* 状态卡片 */
.status-cards {
  margin-bottom: 20px;
}

.status-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border-top: 4px solid #909399;
  transition: all 0.3s;
}

.status-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.status-card.status-high {
  border-top-color: #67c23a;
}

.status-card.status-normal {
  border-top-color: #e6a23c;
}

.status-card.status-low {
  border-top-color: #f56c6c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-content {
  margin-bottom: 16px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f7fa;
}

.metric-row:last-child {
  border-bottom: none;
}

.metric-label {
  font-size: 13px;
  color: #909399;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.metric-value.highlight {
  color: #409EFF;
  font-size: 22px;
}

.metric-value.positive {
  color: #67c23a;
}

.metric-value.negative {
  color: #f56c6c;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* 监控卡片 */
.monitor-card, .record-card {
  margin-bottom: 20px;
  border: none;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 额度监控 */
.quota-monitor {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.quota-item {
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
}

.quota-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.insurer-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  min-width: 80px;
}

.quota-info {
  font-size: 13px;
  color: #606266;
  flex: 1;
  margin-left: 16px;
}

.quota-info strong {
  color: #303133;
}

.warning-icon {
  margin-left: 4px;
  color: #f56c6c;
}

.adjustment-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.adjust-positive {
  background: #f0f9ff;
  color: #409EFF;
}

.adjust-negative {
  background: #fef0f0;
  color: #f56c6c;
}

.adjust-neutral {
  background: #f5f7fa;
  color: #909399;
}

.progress-bar {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.progress-fill.usage-green {
  background: #67c23a;
}

.progress-fill.usage-yellow {
  background: #e6a23c;
}

.progress-fill.usage-orange {
  background: #e6a23c;
}

.progress-fill.usage-red {
  background: #f56c6c;
}

/* 赔付率监控 */
.loss-ratio-monitor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.loss-item {
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
}

.loss-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loss-info {
  font-size: 13px;
  color: #606266;
  flex: 1;
  margin-left: 16px;
}

.loss-info strong {
  color: #303133;
}

.positive {
  color: #67c23a;
  font-weight: 600;
}

.negative {
  color: #f56c6c;
  font-weight: 600;
}

/* 表格样式 */
:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}
</style>
