<template>
  <div class="strategy-confirm-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1>步骤 4：确认保存</h1>
        <p class="description">请确认以下策略信息无误后保存</p>
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
      <div class="step-item">
        <div class="step-icon">3</div>
        <div class="step-label">收益模拟</div>
      </div>
      <div class="step-line"></div>
      <div class="step-item active">
        <div class="step-icon">4</div>
        <div class="step-label">确认保存</div>
      </div>
    </div>

    <!-- 策略基本信息 -->
    <div class="confirm-section">
      <div class="section-header">
        <div class="header-left">
          <div class="section-indicator"></div>
          <h3>策略基本信息</h3>
        </div>
      </div>
      <div class="info-grid">
        <div class="info-item">
          <div class="info-label">策略名称</div>
          <div class="info-value">{{ strategyData.name || '未命名策略' }}</div>
        </div>
        <div class="info-item">
          <div class="info-label">生效机构</div>
          <div class="info-value">{{ (strategyData.institutions || []).join('、') || '全部机构' }}</div>
        </div>
        <div class="info-item full-width">
          <div class="info-label">策略描述</div>
          <div class="info-value">{{ strategyData.description || '无' }}</div>
        </div>
      </div>
    </div>

    <!-- 业务单元列表及模拟结果 -->
    <div class="confirm-section">
      <div class="section-header">
        <div class="header-left">
          <div class="section-indicator"></div>
          <h3>业务单元及模拟结果（{{ (strategyData.businessUnits || []).length }}个）</h3>
        </div>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>业务单元名称</th>
              <th class="text-right">保单数</th>
              <th class="text-right">平均保费</th>
              <th class="text-right">保费规模</th>
              <th class="text-right">纯风险成本</th>
              <th class="text-right">预期利润率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="unit in strategyData.businessUnits" :key="unit.unit_id">
              <td class="unit-name">{{ unit.unit_name }}</td>
              <td class="text-right number">{{ unit.policy_count?.toLocaleString() }}</td>
              <td class="text-right number">¥{{ unit.avg_premium?.toLocaleString() || '-' }}</td>
              <td class="text-right number">¥{{ ((unit.policy_count || 0) * (unit.avg_premium || 0) / 10000).toFixed(0) }}万</td>
              <td class="text-right number">¥{{ (unit.rp || (unit.avg_premium * 0.75 || 0)).toFixed(0) }}</td>
              <td class="text-center">
                <span :class="['margin-badge', getMarginClass(unit.profit_margin)]">
                  {{ ((unit.profit_margin || 0) * 100).toFixed(1) }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 全局兜底参数 -->
    <div class="confirm-section">
      <div class="section-header">
        <div class="header-left">
          <div class="section-indicator"></div>
          <h3>全局兜底参数</h3>
        </div>
      </div>
      <div class="params-grid">
        <div class="param-item">
          <div class="param-label">固定成本率</div>
          <div class="param-value">{{ formatPercent(strategyData.globalParams?.fixed_cost_ratio) }}</div>
        </div>
        <div class="param-item">
          <div class="param-label">目标赔付率</div>
          <div class="param-value">{{ formatPercent(strategyData.globalParams?.target_loss_ratio) }}</div>
        </div>
        <div class="param-item">
          <div class="param-label">市场费用率</div>
          <div class="param-value">{{ formatPercent(strategyData.globalParams?.market_expense_ratio) }}</div>
        </div>
        <div class="param-item">
          <div class="param-label">自主系数下限</div>
          <div class="param-value">{{ strategyData.globalParams?.autonomous_discount_min?.toFixed(2) || '-' }}</div>
        </div>
        <div class="param-item">
          <div class="param-label">自主系数上限</div>
          <div class="param-value">{{ strategyData.globalParams?.autonomous_discount_max?.toFixed(2) || '-' }}</div>
        </div>
        <div class="param-item">
          <div class="param-label">反算折扣</div>
          <div class="param-value">
            <span :class="['status-badge', strategyData.globalParams?.is_calculate ? 'success' : 'default']">
              {{ strategyData.globalParams?.is_calculate ? '是' : '否' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 业务单元独立参数 -->
    <div class="confirm-section" v-if="strategyData.businessUnitParams?.length > 0">
      <div class="section-header">
        <div class="header-left">
          <div class="section-indicator primary"></div>
          <h3>业务单元独立参数</h3>
        </div>
        <el-tag type="warning" size="small">独立参数 > 全局参数</el-tag>
      </div>
      <div class="units-params-list">
        <div 
          v-for="unit in strategyData.businessUnitParams" 
          :key="unit.unit_id"
          class="unit-param-item"
        >
          <div class="unit-param-header">
            <span class="unit-name">{{ unit.unit_name }}</span>
          </div>
          <div class="unit-params-grid">
            <div class="unit-param-item">
              <span class="unit-param-label">固定成本率:</span>
              <span class="unit-param-value">{{ formatPercent(unit.fixed_cost_ratio) }}</span>
            </div>
            <div class="unit-param-item">
              <span class="unit-param-label">目标赔付率:</span>
              <span class="unit-param-value">{{ formatPercent(unit.target_loss_ratio) }}</span>
            </div>
            <div class="unit-param-item">
              <span class="unit-param-label">市场费用率:</span>
              <span class="unit-param-value">{{ formatPercent(unit.market_expense_ratio) }}</span>
            </div>
            <div class="unit-param-item">
              <span class="unit-param-label">自主系数:</span>
              <span class="unit-param-value">
                {{ unit.autonomous_discount_min?.toFixed(2) }} - {{ unit.autonomous_discount_max?.toFixed(2) }}
              </span>
            </div>
            <div class="unit-param-item">
              <span class="unit-param-label">反算折扣:</span>
              <span class="unit-param-value">
                <span :class="['status-badge', unit.is_calculate ? 'success' : 'default']">
                  {{ unit.is_calculate ? '是' : '否' }}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 提示信息 -->
    <el-alert
      title="保存后策略将进入草稿状态，您可以后续进行修改、测试和发布操作。"
      type="info"
      :closable="false"
      show-icon
      class="tip-alert"
    />

    <!-- 底部操作按钮 -->
    <div class="footer-actions">
      <el-button @click="handleBack">上一步</el-button>
      <div class="footer-right">
        <el-button type="success" @click="handleSave">确认保存</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  strategyData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['back', 'save'])

// 格式化百分比
const formatPercent = (value) => {
  if (value === null || value === undefined) return '-'
  return `${(value * 100).toFixed(1)}%`
}

// 获取利润率样式类
const getMarginClass = (margin) => {
  if (!margin) return 'low'
  if (margin >= 0.06) return 'high'
  if (margin >= 0.03) return 'medium'
  if (margin >= 0) return 'low'
  return 'negative'
}

const handleBack = () => {
  emit('back')
}

const handleSave = () => {
  emit('save')
}
</script>

<style scoped>
.strategy-confirm-page {
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

/* 确认区域 */
.confirm-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
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

.section-indicator.primary {
  background: #712ae2;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.info-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
  font-weight: 600;
}

.info-value {
  font-size: 13px;
  color: #303133;
  font-weight: 600;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1px;
  background: #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.info-item {
  background: white;
  padding: 16px 20px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
  font-weight: 600;
}

.info-value {
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

/* 表格 */
.table-container {
  padding: 0 20px 20px;
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
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  font-size: 13px;
}

.unit-name {
  font-weight: 600;
  color: #303133;
}

.number {
  font-family: 'Segoe UI', Arial, sans-serif;
  font-weight: 600;
  color: #303133;
}

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
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

/* 参数网格 */
.params-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1px;
  background: #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  padding: 20px;
}

.param-item {
  background: white;
  padding: 16px;
  text-align: center;
  border-radius: 4px;
}

.param-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
  font-weight: 600;
}

.param-value {
  font-size: 14px;
  font-weight: 700;
  color: #303133;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
}

.status-badge.success {
  background: #f0f9eb;
  color: #67c23a;
}

.status-badge.default {
  background: #f5f7fa;
  color: #909399;
}

/* 业务单元独立参数 */
.units-params-list {
  padding: 20px;
}

.unit-param-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.unit-param-item:last-child {
  margin-bottom: 0;
}

.unit-param-header {
  margin-bottom: 12px;
}

.unit-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.unit-params-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.unit-param-item {
  background: white;
  padding: 12px;
  border-radius: 6px;
}

.unit-param-label {
  font-size: 10px;
  color: #909399;
  margin-bottom: 4px;
  display: block;
}

.unit-param-value {
  font-size: 12px;
  font-weight: 600;
  color: #303133;
  font-family: 'Segoe UI', Arial, sans-serif;
}

/* 提示信息 */
.tip-alert {
  margin-bottom: 20px;
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
