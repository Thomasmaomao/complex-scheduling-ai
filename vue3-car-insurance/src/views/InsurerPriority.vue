<template>
  <div class="insurer-priority-page">
    <div class="page-header">
      <h1>🏢 保司配置中心 - 优先级配置</h1>
      <p>配置各保司的合作目标和调整规则，系统将根据规则自动调整推荐优先级</p>
    </div>

    <!-- 保司列表 -->
    <el-card class="insurer-card">
      <template #header>
        <div class="card-header">
          <h3>保司列表</h3>
          <el-button type="primary" size="small" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加保司
          </el-button>
        </div>
      </template>

      <div class="insurer-list">
        <div v-for="insurer in insurers" :key="insurer.id" class="insurer-item">
          <div class="insurer-summary" @click="toggleExpand(insurer.id)">
            <el-icon class="expand-icon" :class="{ expanded: insurer.expanded }">
              <ArrowRight />
            </el-icon>
            <el-icon v-if="insurer.status === 'active'" class="status-icon status-active"><CircleCheckFilled /></el-icon>
            <el-icon v-else-if="insurer.status === 'paused'" class="status-icon status-paused"><WarningFilled /></el-icon>
            <el-icon v-else class="status-icon status-terminated"><CircleCloseFilled /></el-icon>
            <span class="insurer-name">{{ insurer.name }}</span>
            <div class="insurer-meta">
              <span class="meta-item">基础优先级：<strong>{{ insurer.base_priority }}</strong></span>
              <span class="meta-item">额度目标：<strong>¥{{ insurer.quota_target }}万</strong></span>
              <span class="meta-item">赔付率目标：<strong>{{ insurer.loss_ratio_target }}%</strong></span>
            </div>
          </div>

          <!-- 展开详细配置 -->
          <div v-show="insurer.expanded" class="insurer-detail">
            <div class="detail-section">
              <h4>基础配置</h4>
              <el-form :model="insurer" label-width="100px" size="small">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="基础优先级">
                      <el-input-number 
                        v-model="insurer.base_priority" 
                        :min="0" :max="100" 
                        :step="1"
                        :precision="0"
                        style="width: 150px"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="合作状态">
                      <el-radio-group v-model="insurer.status">
                        <el-radio value="active">正常合作</el-radio>
                        <el-radio value="paused">暂停合作</el-radio>
                        <el-radio value="terminated">终止合作</el-radio>
                      </el-radio-group>
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form>
            </div>

            <div class="detail-section">
              <h4>目标配置</h4>
              <el-form :model="insurer" label-width="100px" size="small">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="额度目标">
                      <el-input-number 
                        v-model="insurer.quota_target" 
                        :min="0" 
                        :step="100"
                        :precision="0"
                        style="width: 150px"
                      />
                      <span class="unit-text">万</span>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="赔付率目标">
                      <el-input-number 
                        v-model="insurer.loss_ratio_target" 
                        :min="0" :max="100" 
                        :step="1"
                        :precision="0"
                        style="width: 150px"
                      />
                      <span class="unit-text">%</span>
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form>
            </div>

            <div class="detail-section">
              <h4>自动调整规则</h4>
              <div class="rules-container">
                <div class="rules-group">
                  <h5>额度使用率规则</h5>
                  <div v-for="(rule, index) in insurer.quota_rules" :key="'quota-'+index" class="rule-item">
                    <el-checkbox v-model="rule.enabled" />
                    <span>使用率 ></span>
                    <el-input-number v-model="rule.threshold" :min="0" :max="100" :step="5" :precision="0" size="small" style="width: 100px" />
                    <span>% → ×</span>
                    <el-input-number v-model="rule.adjustment" :min="0" :max="2" :step="0.05" :precision="2" size="small" style="width: 100px" />
                    <span>（{{ getAdjustmentText(rule.adjustment) }}）</span>
                    <el-button type="danger" link size="small" @click="removeRule(insurer.quota_rules, index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  <el-button type="primary" link size="small" @click="addRule(insurer.quota_rules, 'quota')">
                    <el-icon><Plus /></el-icon> 添加规则
                  </el-button>
                </div>

                <div class="rules-group">
                  <h5>赔付率规则</h5>
                  <div v-for="(rule, index) in insurer.loss_ratio_rules" :key="'loss-'+index" class="rule-item">
                    <el-checkbox v-model="rule.enabled" />
                    <span>赔付率 ></span>
                    <el-input-number v-model="rule.threshold" :min="0" :max="100" :step="5" :precision="0" size="small" style="width: 100px" />
                    <span>% → ×</span>
                    <el-input-number v-model="rule.adjustment" :min="0" :max="2" :step="0.05" :precision="2" size="small" style="width: 100px" />
                    <span>（{{ getAdjustmentText(rule.adjustment) }}）</span>
                    <el-button type="danger" link size="small" @click="removeRule(insurer.loss_ratio_rules, index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  <el-button type="primary" link size="small" @click="addRule(insurer.loss_ratio_rules, 'loss')">
                    <el-icon><Plus /></el-icon> 添加规则
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 底部按钮 -->
    <div class="fixed-actions">
      <el-button @click="showBatchEditDialog">批量编辑规则</el-button>
      <el-button type="success" @click="saveConfig">保存配置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus, Delete, ArrowRight, CircleCheckFilled, WarningFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 保司数据
const insurers = reactive([
  {
    id: 1,
    name: '保司 A',
    status: 'active',
    base_priority: 80,
    quota_target: 1000,
    loss_ratio_target: 75,
    expanded: false,
    quota_rules: [
      { enabled: true, threshold: 80, adjustment: 0.80 },
      { enabled: true, threshold: 100, adjustment: 0.50 },
      { enabled: true, threshold: 50, adjustment: 1.20 }
    ],
    loss_ratio_rules: [
      { enabled: true, threshold: 80, adjustment: 0.85 },
      { enabled: true, threshold: 90, adjustment: 0.70 }
    ]
  },
  {
    id: 2,
    name: '保司 B',
    status: 'active',
    base_priority: 75,
    quota_target: 800,
    loss_ratio_target: 75,
    expanded: false,
    quota_rules: [
      { enabled: true, threshold: 80, adjustment: 0.80 },
      { enabled: true, threshold: 100, adjustment: 0.50 },
      { enabled: true, threshold: 50, adjustment: 1.20 }
    ],
    loss_ratio_rules: [
      { enabled: true, threshold: 80, adjustment: 0.85 },
      { enabled: true, threshold: 90, adjustment: 0.70 }
    ]
  },
  {
    id: 3,
    name: '保司 C',
    status: 'active',
    base_priority: 85,
    quota_target: 1200,
    loss_ratio_target: 75,
    expanded: false,
    quota_rules: [
      { enabled: true, threshold: 80, adjustment: 0.80 },
      { enabled: true, threshold: 100, adjustment: 0.50 },
      { enabled: true, threshold: 50, adjustment: 1.20 }
    ],
    loss_ratio_rules: [
      { enabled: true, threshold: 80, adjustment: 0.85 },
      { enabled: true, threshold: 90, adjustment: 0.70 }
    ]
  }
])

// 切换展开状态
const toggleExpand = (id) => {
  const insurer = insurers.find(i => i.id === id)
  if (insurer) {
    insurer.expanded = !insurer.expanded
  }
}

// 获取调整文字说明
const getAdjustmentText = (adjustment) => {
  if (adjustment > 1) {
    return `上调${((adjustment - 1) * 100).toFixed(0)}%`
  } else if (adjustment < 1) {
    return `下调${((1 - adjustment) * 100).toFixed(0)}%`
  }
  return '不变'
}

// 添加规则
const addRule = (rules, type) => {
  if (type === 'quota') {
    rules.push({ enabled: true, threshold: 80, adjustment: 0.80 })
  } else {
    rules.push({ enabled: true, threshold: 80, adjustment: 0.85 })
  }
}

// 删除规则
const removeRule = (rules, index) => {
  rules.splice(index, 1)
}

// 显示添加保司对话框
const showAddDialog = () => {
  ElMessage.info('添加保司功能开发中...')
}

// 显示批量编辑对话框
const showBatchEditDialog = () => {
  ElMessage.info('批量编辑规则功能开发中...')
}

// 保存配置
const saveConfig = () => {
  console.log('保存配置:', insurers)
  ElMessage.success('配置已保存')
}
</script>

<style scoped>
.insurer-priority-page {
  padding: 16px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  margin-bottom: 16px;
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

.insurer-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insurer-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.insurer-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.insurer-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.3s;
}

.insurer-summary:hover {
  background: #f5f7fa;
}

.expand-icon {
  font-size: 16px;
  color: #909399;
  transition: transform 0.3s;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.status-icon {
  font-size: 18px;
}

.status-active {
  color: #67c23a;
}

.status-paused {
  color: #e6a23c;
}

.status-terminated {
  color: #f56c6c;
}

.insurer-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  min-width: 100px;
}

.insurer-meta {
  display: flex;
  gap: 16px;
  margin-left: auto;
  font-size: 12px;
}

.meta-item {
  color: #606266;
}

.meta-item strong {
  color: #303133;
  font-weight: 600;
}

.insurer-detail {
  padding: 16px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  padding-left: 10px;
  border-left: 3px solid #409EFF;
}

.rules-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.rules-group {
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
}

.rules-group h5 {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  margin: 0 0 10px 0;
}

.rule-item {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
}

.rule-item:last-child {
  margin-bottom: 0;
}

@media (max-width: 1200px) {
  .rules-container {
    grid-template-columns: 1fr;
  }
}

.unit-text {
  margin-left: 8px;
  font-size: 13px;
  color: #909399;
}

.fixed-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}
</style>
