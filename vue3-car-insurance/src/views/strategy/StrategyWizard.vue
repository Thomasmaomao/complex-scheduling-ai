<template>
  <div class="strategy-wizard-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>{{ isEdit ? '编辑策略' : '新建策略' }}</h1>
      <p class="page-description">{{ isEdit ? '修改现有策略配置' : '创建新的车险定价策略' }}</p>
    </div>

    <!-- 专业步骤进度条 -->
    <el-card class="steps-card">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step
          v-for="(step, idx) in steps"
          :key="idx"
          :title="step.title"
          :description="step.desc"
        >
          <template #icon>
            <el-icon v-if="currentStep > idx" color="#67c23a"><Check /></el-icon>
            <span v-else-if="currentStep === idx" class="step-number-active">{{ idx + 1 }}</span>
            <span v-else class="step-number">{{ idx + 1 }}</span>
          </template>
        </el-step>
      </el-steps>
    </el-card>

    <!-- 步骤内容区域 -->
    <el-card class="content-card">
      <!-- 步骤 1：基本信息 -->
      <div v-show="currentStep === 0" class="step-panel">
        <div class="panel-header">
          <el-icon><Document /></el-icon>
          <h2>基本信息</h2>
          <span class="panel-subtitle">填写策略名称和生效机构</span>
        </div>

        <el-form :model="formData" label-width="140px" label-position="left" class="basic-form" style="max-width: 1000px;">
          <el-form-item label="策略名称 *" required>
            <el-input
              v-model="formData.name"
              placeholder="请输入策略名称，如：燃油车续保策略"
              maxlength="200"
              show-word-limit
              class="form-input-large"
            />
          </el-form-item>

          <el-form-item label="策略描述">
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="4"
              placeholder="请输入策略描述（可选）"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="生效机构 *" required>
            <div class="institution-row">
              <el-checkbox-group v-model="formData.institutions">
                <el-checkbox
                  v-for="inst in institutions"
                  :key="inst"
                  :value="inst"
                  border
                  class="institution-checkbox-inline"
                >
                  {{ inst }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </el-form-item>

          <el-alert
            v-if="formData.institutions.length === 0"
            title="请至少选择一个生效机构"
            type="warning"
            :closable="false"
            show-icon
            class="mt-4"
          />
        </el-form>

        <div class="fixed-actions">
          <el-button @click="reset">重置</el-button>
          <el-button type="primary" @click="nextStep">
            下一步：业务单元划分
            <el-icon class="ml-1"><Arrow-Right /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 步骤 2：业务单元划分 -->
      <div v-show="currentStep === 1" class="step-panel">
        <div class="panel-header">
          <el-icon><Data-Board /></el-icon>
          <h2>业务单元划分</h2>
          <span class="panel-subtitle">选择需要纳入策略的业务单元</span>
        </div>

        <div class="section-toolbar">
          <div class="toolbar-left">
            <h3>业务单元列表</h3>
          </div>
          <el-button size="small" @click="handleSelectAll">
            {{ allSelected ? '取消全选' : '全选' }}
          </el-button>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th class="text-center" style="width:50px">选择</th>
                <th>业务单元 ID</th>
                <th>业务单元名称</th>
                <th>说明</th>
                <th class="text-right">保单数</th>
                <th class="text-right">平均保费</th>
                <th class="text-right">保费规模</th>
                <th class="text-center">预期利润率</th>
                <th class="text-center">策略建议</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="unit in allBusinessUnits" :key="unit.unit_id" :class="['table-row', isSelected(unit) ? 'selected' : '']">
                <td class="text-center">
                  <input type="checkbox" :checked="isSelected(unit)" @change="toggleSelection(unit)" />
                </td>
                <td class="unit-id">{{ unit.unit_id }}</td>
                <td class="unit-name">{{ unit.unit_name }}</td>
                <td class="unit-desc">{{ unit.description || '-' }}</td>
                <td class="text-right number">{{ unit.policy_count?.toLocaleString() }}</td>
                <td class="text-right number">¥{{ unit.avg_premium?.toLocaleString() || '-' }}</td>
                <td class="text-right number">¥{{ (unit.premium_scale / 10000).toFixed(0) }}万</td>
                <td class="text-center">
                  <span class="margin-badge" :class="getMarginClass(unit.expected_profit_margin)">
                    {{ (unit.expected_profit_margin * 100).toFixed(1) }}%
                  </span>
                </td>
                <td class="text-center">
                  <span class="suggestion-badge" :class="getSuggestionClass(unit.strategy_suggestion)">
                    {{ unit.strategy_suggestion }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="summary-section" v-if="selectedUnits.length > 0">
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="summary-card-stat">
                <div class="stat-icon policies"><el-icon><User /></el-icon></div>
                <div class="stat-content">
                  <div class="stat-label">总保单数</div>
                  <div class="stat-value">{{ totalPolicies.toLocaleString() }}<span class="stat-unit">单</span></div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-card-stat">
                <div class="stat-icon premium"><el-icon><Money /></el-icon></div>
                <div class="stat-content">
                  <div class="stat-label">总保费规模</div>
                  <div class="stat-value">¥{{ (totalPremium / 10000).toFixed(0) }}<span class="stat-unit">万</span></div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-card-stat">
                <div class="stat-icon margin"><el-icon><Trend-Charts /></el-icon></div>
                <div class="stat-content">
                  <div class="stat-label">平均预期利润率</div>
                  <div class="stat-value">{{ avgProfitMargin.toFixed(1) }}<span class="stat-unit">%</span></div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-card-stat">
                <div class="stat-icon risk" :class="getRiskClass(overallRiskLevel)"><el-icon><Warning /></el-icon></div>
                <div class="stat-content">
                  <div class="stat-label">整体风险等级</div>
                  <div class="stat-value" :class="getRiskClass(overallRiskLevel)">{{ overallRiskLevel }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <div class="fixed-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" @click="nextStep">
            下一步：成本模拟
            <el-icon class="ml-1"><Arrow-Right /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 步骤 3：成本模拟 -->
      <div v-show="currentStep === 2" class="step-panel">
        <div class="panel-header">
          <el-icon><Setting /></el-icon>
          <h2>成本模拟</h2>
          <span class="panel-subtitle">配置全局参数和业务单元独立参数</span>
        </div>

        <el-empty v-if="selectedUnits.length === 0" description="请先在业务单元划分步骤选择业务单元" />

        <template v-else>
          <!-- 全局兜底参数 -->
          <div class="section-title">
            <el-icon><Setting /></el-icon>
            <h3>全局兜底参数</h3>
          </div>
          <el-card class="global-params-card mb-4">
            <el-form :inline="true" class="params-form">
              <el-form-item label="固定成本率">
                <el-input-number 
                  v-model="fixedCostRatio" 
                  :min="0" :max="1" :step="0.01" :precision="2"
                  controls-position="right"
                  style="width: 100px;"
                  @change="handleGlobalParamChange"
                />
              </el-form-item>
              <el-form-item label="目标赔付率">
                <el-input-number 
                  v-model="targetLossRatio" 
                  :min="0" :max="1" :step="0.01" :precision="2"
                  controls-position="right"
                  style="width: 100px;"
                  @change="handleGlobalParamChange"
                />
              </el-form-item>
              <el-form-item label="市场费用率">
                <el-input-number 
                  v-model="marketExpenseRatio" 
                  :min="0" :max="1" :step="0.01" :precision="2"
                  controls-position="right"
                  style="width: 100px;"
                  @change="handleGlobalParamChange"
                />
              </el-form-item>
              <el-form-item label="自主系数下限">
                <el-input-number 
                  v-model="autonomousDiscountMin" 
                  :min="0.5" :max="1.5" :step="0.01" :precision="2"
                  controls-position="right"
                  style="width: 100px;"
                  @change="handleGlobalParamChange"
                />
              </el-form-item>
              <el-form-item label="自主系数上限">
                <el-input-number 
                  v-model="autonomousDiscountMax" 
                  :min="0.5" :max="1.5" :step="0.01" :precision="2"
                  controls-position="right"
                  style="width: 100px;"
                  @change="handleGlobalParamChange"
                />
              </el-form-item>
              <el-form-item label="反算折扣">
                <el-switch v-model="isCalculate" active-text="是" inactive-text="否" />
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 业务单元独立参数 -->
          <div class="section-title-with-action">
            <div class="section-title-left">
              <el-icon><Data-Board /></el-icon>
              <h3>业务单元成本模拟</h3>
            </div>
            <el-button type="primary" size="small" @click="calculateAll">
              <el-icon><Refresh /></el-icon>
              成本测算
            </el-button>
          </div>
          <el-card class="unit-params-card mb-4">
            <el-table :data="businessUnitParams" border stripe>
              <el-table-column prop="unit_name" label="业务单元" />
              <el-table-column prop="policies" label="保单数" align="right">
                <template #default="{ row }">{{ row.policies?.toLocaleString() }}</template>
              </el-table-column>
              <el-table-column label="平均保费" align="right">
                <template #default="{ row }">¥{{ (row.avg_premium || 0).toLocaleString() }}</template>
              </el-table-column>
              <el-table-column label="纯风险成本" align="right">
                <template #default="{ row }">¥{{ (row.pure_risk_cost || 0).toFixed(0) }}</template>
              </el-table-column>
              <el-table-column label="自主系数下限" align="center">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.autonomous_discount_min"
                    :min="0.5" :max="1.5" :step="0.01"
                    controls-position="right"
                    size="small"
                    style="width: 100%"
                    @change="handleUnitParamChange(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="自主系数上限" align="center">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.autonomous_discount_max"
                    :min="0.5" :max="1.5" :step="0.01"
                    controls-position="right"
                    size="small"
                    style="width: 100%"
                    @change="handleUnitParamChange(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="固定成本率" align="center">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.fixed_cost_ratio"
                    :min="0" :max="1" :step="0.01"
                    controls-position="right"
                    size="small"
                    style="width: 100%"
                    @change="handleUnitParamChange(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="目标赔付率" align="center">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.target_loss_ratio"
                    :min="0" :max="1" :step="0.01"
                    controls-position="right"
                    size="small"
                    style="width: 100%"
                    @change="handleUnitParamChange(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="市场费用率" align="center">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.market_expense_ratio"
                    :min="0" :max="1" :step="0.01"
                    controls-position="right"
                    size="small"
                    style="width: 100%"
                    @change="handleUnitParamChange(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="预期利润率" align="center">
                <template #default="{ row }">
                  <span :class="getProfitMarginClass(row.expected_profit_margin * 100)">
                    {{ (row.expected_profit_margin * 100).toFixed(1) }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="" width="60" align="center">
                <template #default="{ row }">
                  <el-checkbox
                    v-model="row.use_global"
                    @change="handleUseGlobalChange(row)"
                  />
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <!-- 实时计算汇总指标 -->
          <div class="section-title">
            <el-icon><Trend-Charts /></el-icon>
            <h3>实时汇总指标</h3>
          </div>
          <el-card class="summary-metrics-card">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-label">总保单数</div>
                  <div class="metric-value">{{ totalPolicies.toLocaleString() }}<span class="metric-unit">单</span></div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-label">总保费</div>
                  <div class="metric-value">¥{{ (totalPremium / 10000).toFixed(0) }}<span class="metric-unit">万</span></div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-label">总纯风险成本</div>
                  <div class="metric-value">¥{{ totalPureRiskCost.toFixed(0) }}<span class="metric-unit">万</span></div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-label">整体利润率</div>
                  <div class="metric-value">{{ profitMargin.toFixed(1) }}<span class="metric-unit">%</span></div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </template>

        <div class="fixed-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" @click="nextStep">
            下一步：收益模拟
            <el-icon class="ml-1"><Arrow-Right /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 步骤 4：收益模拟 -->
      <div v-show="currentStep === 3" class="step-panel">
        <div class="panel-header">
          <el-icon><Trend-Charts /></el-icon>
          <h2>收益模拟</h2>
          <span class="panel-subtitle">多情景模拟和收益测算</span>
        </div>

        <el-empty v-if="selectedUnits.length === 0" description="请先在业务单元划分步骤选择业务单元" />

        <template v-else>
          <!-- 业务单元收益表格 -->
          <el-card class="detail-card">
            <template #header>
              <div class="card-header-with-actions">
                <span><el-icon><Data-Board /></el-icon> 各业务单元预期收益</span>
                <el-button type="primary" size="small" @click="overallCalculate">
                  <el-icon><Refresh /></el-icon>
                  整体测算
                </el-button>
              </div>
            </template>
            <el-table :data="businessUnitParams" border stripe>
              <el-table-column type="expand" width="50">
                <template #default="{ row, $index }">
                  <div v-show="scenarioExpanded[$index]" class="scenario-expand-content">
                    <div class="scenario-cards-grid-simple">
                      <div
                        v-for="scenario in scenarios"
                        :key="scenario.id"
                        :class="['scenario-card-simple', row.selectedScenario === scenario.id ? 'active' : '']"
                      >
                        <div class="scenario-card-header-simple">
                          <span class="scenario-name-simple">{{ scenario.name }}</span>
                          <el-tag v-if="row.selectedScenario === scenario.id" type="success" size="small">已应用</el-tag>
                        </div>
                        <div class="scenario-metrics-simple">
                          <div class="metric-simple">
                            <span class="metric-label-simple">保单数</span>
                            <span class="metric-value-simple">{{ calculateScenarioPolicyCount(row, scenario.id).toLocaleString() }}单</span>
                          </div>
                          <div class="metric-simple">
                            <span class="metric-label-simple">保费</span>
                            <span class="metric-value-simple">¥{{ calculateScenarioPremium(row, scenario.id).toFixed(0) }}万</span>
                          </div>
                          <div class="metric-simple">
                            <span class="metric-label-simple">利润</span>
                            <span class="metric-value-simple" :class="calculateScenarioProfit(row, scenario.id) >= 0 ? 'positive' : 'negative'">
                              ¥{{ calculateScenarioProfit(row, scenario.id).toFixed(0) }}万
                            </span>
                          </div>
                          <div class="metric-simple">
                            <span class="metric-label-simple">利润率</span>
                            <span class="metric-value-simple" :class="getMarginClass(calculateScenarioMargin(row, scenario.id))">
                              {{ (calculateScenarioMargin(row, scenario.id) * 100).toFixed(1) }}%
                            </span>
                          </div>
                        </div>
                        <el-button
                          type="primary"
                          size="small"
                          @click="applyScenario(row, scenario.id)"
                          :disabled="row.selectedScenario === scenario.id"
                          class="scenario-apply-btn"
                        >
                          {{ row.selectedScenario === scenario.id ? '已应用' : '应用此情景' }}
                        </el-button>
                      </div>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="unit_name" label="业务单元" />
              <el-table-column prop="policies" label="保单数" align="right">
                <template #default="{ row }">{{ row.policies?.toLocaleString() }}</template>
              </el-table-column>
              <el-table-column label="平均保费" align="right">
                <template #default="{ row }">¥{{ (row.avg_premium || 0).toLocaleString() }}</template>
              </el-table-column>
              <el-table-column label="纯风险成本" align="right">
                <template #default="{ row }">¥{{ (row.pure_risk_cost || 0).toFixed(0) }}</template>
              </el-table-column>
              <el-table-column label="预期利润率" align="center">
                <template #default="{ row }">
                  <span :class="getProfitMarginClass(row.expected_profit_margin * 100)">
                    {{ (row.expected_profit_margin * 100).toFixed(1) }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="多情景模拟" width="120" align="center">
                <template #default="{ row, $index }">
                  <el-button
                    size="small"
                    :type="scenarioExpanded[$index] ? 'primary' : 'default'"
                    @click="toggleScenario($index)"
                  >
                    {{ scenarioExpanded[$index] ? '收起情景' : '展开情景' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <!-- 底部汇总指标（与成本模拟一致） -->
          <el-card class="summary-metrics-card mt-4">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="metric-item primary">
                  <div class="metric-icon"><el-icon><User /></el-icon></div>
                  <div class="metric-content">
                    <div class="metric-label">总保单数</div>
                    <div class="metric-value">{{ totalPolicies.toLocaleString() }}<span class="metric-unit">单</span></div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item success">
                  <div class="metric-icon"><el-icon><Money /></el-icon></div>
                  <div class="metric-content">
                    <div class="metric-label">总保费</div>
                    <div class="metric-value">¥{{ (totalPremium / 10000).toFixed(0) }}<span class="metric-unit">万</span></div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item warning">
                  <div class="metric-icon"><el-icon><Coin /></el-icon></div>
                  <div class="metric-content">
                    <div class="metric-label">总利润</div>
                    <div class="metric-value positive">¥{{ totalProfit.toFixed(0) }}<span class="metric-unit">万</span></div>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item info">
                  <div class="metric-icon"><el-icon><Trend-Charts /></el-icon></div>
                  <div class="metric-content">
                    <div class="metric-label">整体利润率</div>
                    <div class="metric-value">{{ profitMargin.toFixed(1) }}<span class="metric-unit">%</span></div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </template>

        <div class="fixed-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" @click="nextStep">
            下一步：确认保存
            <el-icon class="ml-1"><Arrow-Right /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 步骤 5：确认保存 -->
      <div v-show="currentStep === 4" class="step-panel">
        <div class="panel-header">
          <el-icon><Document-Checked /></el-icon>
          <h2>确认保存</h2>
          <span class="panel-subtitle">请确认策略信息无误后保存</span>
        </div>

        <!-- 策略摘要卡片 -->
        <div class="section-title">
          <el-icon><Document /></el-icon>
          <h3>策略摘要</h3>
        </div>
        <el-card class="strategy-summary-card mb-4">
          <el-descriptions :column="6" border size="small">
            <el-descriptions-item label="策略名称" label-class-name="desc-label-small">
              <span class="desc-value-small">{{ formData.name }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="生效机构" label-class-name="desc-label-small" :span="2">
              <span class="desc-value-small">{{ formData.institutions.join('、') }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="策略描述" label-class-name="desc-label-small" :span="3">
              <span class="desc-value-small">{{ formData.description || '无' }}</span>
            </el-descriptions-item>
          </el-descriptions>

          <div class="params-subsection-compact">
            <h4>全局兜底参数</h4>
            <el-descriptions :column="6" border size="small">
              <el-descriptions-item label="固定成本率" label-class-name="desc-label-small">
                <span class="desc-value-small">{{ (globalParams.fixed_cost_ratio * 100).toFixed(1) }}%</span>
              </el-descriptions-item>
              <el-descriptions-item label="目标赔付率" label-class-name="desc-label-small">
                <span class="desc-value-small">{{ (globalParams.target_loss_ratio * 100).toFixed(1) }}%</span>
              </el-descriptions-item>
              <el-descriptions-item label="市场费用率" label-class-name="desc-label-small">
                <span class="desc-value-small">{{ (globalParams.market_expense_ratio * 100).toFixed(1) }}%</span>
              </el-descriptions-item>
              <el-descriptions-item label="自主系数下限" label-class-name="desc-label-small">
                <span class="desc-value-small">{{ globalParams.autonomous_discount_min.toFixed(2) }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="自主系数上限" label-class-name="desc-label-small">
                <span class="desc-value-small">{{ globalParams.autonomous_discount_max.toFixed(2) }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="反算折扣" label-class-name="desc-label-small">
                <span class="desc-value-small">{{ globalParams.is_calculate ? '是' : '否' }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>

        <!-- 业务单元模拟结果表格 -->
        <div class="section-title" v-if="selectedUnits.length > 0">
          <el-icon><Data-Board /></el-icon>
          <h3>业务单元模拟结果</h3>
        </div>
        <el-card class="business-units-summary-card mb-4" v-if="selectedUnits.length > 0">
          <el-table :data="businessUnitParams" border stripe>
            <el-table-column prop="unit_name" label="业务单元" />
            <el-table-column prop="policies" label="保单数" align="right">
              <template #default="{ row }">{{ row.policies?.toLocaleString() }}</template>
            </el-table-column>
            <el-table-column label="平均保费" align="right">
              <template #default="{ row }">¥{{ (row.avg_premium || 0).toLocaleString() }}</template>
            </el-table-column>
            <el-table-column label="保费规模" align="right">
              <template #default="{ row }">¥{{ calculatePremiumScale(row) }}万</template>
            </el-table-column>
            <el-table-column label="纯风险成本" align="right">
              <template #default="{ row }">¥{{ (row.pure_risk_cost || 0).toFixed(0) }}</template>
            </el-table-column>
            <el-table-column label="预期利润率" align="center">
              <template #default="{ row }">
                <span :class="getProfitMarginClass(row.expected_profit_margin * 100)">
                  {{ (row.expected_profit_margin * 100).toFixed(1) }}%
                </span>
              </template>
            </el-table-column>
          </el-table>

          <!-- 业务单元贡献度分析 -->
          <div class="contribution-section">
            <h4>业务单元贡献度分析</h4>
            <el-table :data="contributionData" size="small" border>
              <el-table-column prop="unit_name" label="业务单元" />
              <el-table-column prop="premiumContribution" label="保费贡献" align="right">
                <template #default="{ row }">{{ row.premiumContribution }}%</template>
              </el-table-column>
              <el-table-column prop="profitContribution" label="利润贡献" align="right">
                <template #default="{ row }">{{ row.profitContribution }}%</template>
              </el-table-column>
              <el-table-column prop="marginContribution" label="利润率贡献" align="right">
                <template #default="{ row }">{{ row.marginContribution }}%</template>
              </el-table-column>
              <el-table-column label="贡献度" align="center">
                <template #default="{ row }">
                  <div class="contribution-bar">
                    <div class="contribution-fill" :style="{ width: row.premiumContribution + '%' }"></div>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 整体合计区域 (移到最后，白色卡片) -->
          <div class="overall-totals-white">
            <div class="totals-title-black">
              <el-icon><Trend-Charts /></el-icon>
              <h4>整体合计</h4>
            </div>
            <el-row :gutter="20" class="totals-grid">
              <el-col :span="5">
                <div class="total-item">
                  <div class="total-label">总保单数</div>
                  <div class="total-value">{{ totalPolicies.toLocaleString() }}<span class="total-unit">单</span></div>
                </div>
              </el-col>
              <el-col :span="5">
                <div class="total-item">
                  <div class="total-label">总保费规模</div>
                  <div class="total-value">¥{{ (totalPremium / 10000).toFixed(0) }}<span class="total-unit">万</span></div>
                </div>
              </el-col>
              <el-col :span="5">
                <div class="total-item">
                  <div class="total-label">总纯风险成本</div>
                  <div class="total-value">¥{{ totalPureRiskCost.toFixed(0) }}<span class="total-unit">万</span></div>
                </div>
              </el-col>
              <el-col :span="5">
                <div class="total-item">
                  <div class="total-label">总预期利润</div>
                  <div class="total-value positive">¥{{ totalProfit.toFixed(0) }}<span class="total-unit">万</span></div>
                </div>
              </el-col>
              <el-col :span="4">
                <div class="total-item">
                  <div class="total-label">整体利润率</div>
                  <div class="total-value">{{ profitMargin.toFixed(1) }}<span class="total-unit">%</span></div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <!-- 提示信息 -->
        <el-alert
          title="保存后策略将进入草稿状态，您可以后续进行修改、测试和发布操作。"
          type="info"
          :closable="false"
          show-icon
          class="mb-4"
        />

        <div class="fixed-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="success" @click="confirmSave">
            <el-icon><Check /></el-icon>
            保存策略
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 编辑业务单元参数弹窗 -->
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

              :step="0.01"
              :min="0.5"
              :max="1.5"
              controls-position="right"
            />
            <span class="range-text">至</span>
            <el-input-number
              v-model="currentUnit.autonomous_discount_max"

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
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Setting, DataBoard, Document, DocumentChecked, Refresh,
  Check, ArrowRight, ArrowDown, User, Money, Coin,
  TrendCharts, Warning
} from '@element-plus/icons-vue'
import { createStrategy, updateStrategy, saveWizardBusinessUnit, saveWizardCostSimulation, saveWizardRevenueSimulation, confirmWizard, getStrategy } from '../../api/strategy'
import { getAllBusinessUnits } from '../../api/businessUnit'

const router = useRouter(), route = useRoute()
const isEdit = computed(() => !!route.params.id)
const currentStep = ref(0)
const steps = [
  { title: '基本信息', desc: '填写策略名称和机构' },
  { title: '业务单元划分', desc: '选择业务单元' },
  { title: '成本模拟', desc: '配置成本参数' },
  { title: '收益模拟', desc: '多情景模拟' },
  { title: '确认保存', desc: '确认并保存' }
]
const institutions = ['上海', '北京', '广东', '浙江', '江苏', '四川']

const formData = reactive({ name: '', description: '', institutions: [] })
// 全局兜底参数 - 使用 ref 确保响应式
// 全局兜底参数 - 使用 ref 定义每个参数
const fixedCostRatio = ref(0.10)
const targetLossRatio = ref(0.75)
const marketExpenseRatio = ref(0.12)
const autonomousDiscountMin = ref(0.70)
const autonomousDiscountMax = ref(1.30)
const isCalculate = ref(true)

// 兼容旧代码的 globalParams 对象（用于业务逻辑）
const globalParams = {
  get fixed_cost_ratio() { return fixedCostRatio.value },
  set fixed_cost_ratio(val) { fixedCostRatio.value = val },
  get target_loss_ratio() { return targetLossRatio.value },
  set target_loss_ratio(val) { targetLossRatio.value = val },
  get market_expense_ratio() { return marketExpenseRatio.value },
  set market_expense_ratio(val) { marketExpenseRatio.value = val },
  get autonomous_discount_min() { return autonomousDiscountMin.value },
  set autonomous_discount_min(val) { autonomousDiscountMin.value = val },
  get autonomous_discount_max() { return autonomousDiscountMax.value },
  set autonomous_discount_max(val) { autonomousDiscountMax.value = val },
  get is_calculate() { return isCalculate.value },
  set is_calculate(val) { isCalculate.value = val }
}

// 默认参数值（用于初始化业务单元）
const defaultGlobalParams = {
  fixed_cost_ratio: 0.10,
  target_loss_ratio: 0.75,
  market_expense_ratio: 0.12,
  autonomous_discount_min: 0.70,
  autonomous_discount_max: 1.30,
  is_calculate: true
}

// 业务单元列表 - 从 API 加载
const allBusinessUnits = ref([])
const loadingBusinessUnits = ref(false)

// 加载业务单元数据
const loadBusinessUnits = async () => {
  loadingBusinessUnits.value = true
  try {
    const response = await getAllBusinessUnits()
    allBusinessUnits.value = (response.business_units || []).map(bu => ({
      ...bu,
      // 字段映射：expected_loss_ratio → target_loss_ratio
      target_loss_ratio: bu.expected_loss_ratio,
      premium_scale: bu.policy_count * bu.avg_premium,  // 计算保费规模
      strategy_suggestion: bu.expected_profit_margin >= 0.05 ? '推荐' : bu.expected_profit_margin >= 0.03 ? '谨慎' : '控制'
    }))
  } catch (error) {
    console.error('加载业务单元失败:', error)
    // 加载失败时使用空数组
    allBusinessUnits.value = []
  } finally {
    loadingBusinessUnits.value = false
  }
}

const selectedUnits = ref([]), businessUnitParams = ref([]), scenarioExpanded = ref([])

// 情景定义
// 业务逻辑：赔付率变化反映风险选择策略
// 赔付率下降（收紧核保）→ 边缘客户被拒 → 保单数小幅减少，利润率上升
// 赔付率上升（放宽核保）→ 接受边缘客户 → 保单数小幅增加，利润率下降
// 利润 = 保费规模 × 利润率 = (保单数 × 平均保费) × 利润率
// 目的：展示不同核保政策下的利润影响，帮助业务决策
const scenarios = [
  { id: 's1', name: '收紧核保 (-4%)', profitAdjust: -0.04, policyAdjust: -0.08 },  // 赔付率降 4%，保单数降 8%
  { id: 's2', name: '轻微收紧 (-2%)', profitAdjust: -0.02, policyAdjust: -0.04 },  // 赔付率降 2%，保单数降 4%
  { id: 'base', name: '当前策略', profitAdjust: 0, policyAdjust: 0 },              // 当前核保政策
  { id: 's4', name: '轻微放宽 (+2%)', profitAdjust: 0.02, policyAdjust: 0.04 },    // 赔付率升 2%，保单数增 4%
  { id: 's5', name: '放宽核保 (+4%)', profitAdjust: 0.04, policyAdjust: 0.08 }     // 赔付率升 4%，保单数增 8%
]

// 编辑弹窗
const editDialogVisible = ref(false)
const currentUnit = ref({})

// 全局参数表格展示数据
const globalParamsTable = computed(() => [
  { label: '固定成本率', value: `${(globalParams.fixed_cost_ratio * 100).toFixed(1)}%` },
  { label: '目标赔付率', value: `${(globalParams.target_loss_ratio * 100).toFixed(1)}%` },
  { label: '市场费用率', value: `${(globalParams.market_expense_ratio * 100).toFixed(1)}%` },
  { label: '自主系数下限', value: globalParams.autonomous_discount_min.toFixed(2) },
  { label: '自主系数上限', value: globalParams.autonomous_discount_max.toFixed(2) },
  { label: '反算折扣', value: globalParams.is_calculate ? '是' : '否' }
])

// 贡献度分析数据
const contributionData = computed(() => {
  if (businessUnitParams.value.length === 0) return []

  const totalPremiumVal = totalPremium.value
  const totalProfitVal = totalProfit.value

  return businessUnitParams.value.map(unit => {
    const unitPremium = (unit.policies * unit.avg_premium) / 10000
    const unitProfit = unitPremium * unit.expected_profit_margin

    return {
      unit_name: unit.unit_name,
      premiumContribution: totalPremiumVal > 0 ? ((unitPremium / (totalPremiumVal / 10000)) * 100).toFixed(1) : 0,
      profitContribution: totalProfitVal > 0 ? ((unitProfit / totalProfitVal) * 100).toFixed(1) : 0,
      marginContribution: (unit.expected_profit_margin * 100).toFixed(1)
    }
  })
})

// 计算保费规模（万元）
const calculatePremiumScale = (row) => {
  if (!row.policies || !row.avg_premium) return 0
  return (row.policies * row.avg_premium) / 10000
}

// 纯风险成本（RP）= 预存值，从业务单元数据中读取
// 注意：RP 是预存的固定值，不是计算出来的
const calculatePureRiskCost = (unit) => {
  // 如果业务单元有预存的 pure_risk_cost，直接使用（单位已经是万元）
  if (unit.pure_risk_cost !== undefined && unit.pure_risk_cost !== null) {
    return unit.pure_risk_cost
  }
  // 否则使用默认值：保单数 × 平均保费 × 目标赔付率 / 10000（万元）
  const params = getEffectiveParams(unit)
  return (unit.policies * unit.avg_premium * (params.target_loss_ratio || 0.75)) / 10000
}

// 获取业务单元的预设纯风险成本（元/单）
const getUnitPureRiskCost = (unit) => {
  // 直接从预设数据读取，如果没有则报错
  if (unit.pure_risk_cost === undefined || unit.pure_risk_cost === null || unit.pure_risk_cost === 0) {
    throw new Error(`业务单元 "${unit.unit_name}" 缺少 pure_risk_cost 预设值`)
  }
  return unit.pure_risk_cost
}

// 获取实际使用的参数（独立参数优先）
const getEffectiveParams = (unit) => {
  if (!unit.use_global && unit.fixed_cost_ratio !== undefined) {
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

// 计算边际成本率 = 目标赔付率 + 市场费用率
const calculateMarginCostRate = (row) => {
  const params = getEffectiveParams(row)
  return (params.target_loss_ratio || 0) + (params.market_expense_ratio || 0)
}

// 计算利润率 = 1 - 边际成本率 - 固定成本率
const calculateProfitMargin = (row) => {
  const params = getEffectiveParams(row)
  const marginCostRate = calculateMarginCostRate(row)
  return 1 - marginCostRate - (params.fixed_cost_ratio || 0)
}

// 计算预期利润（万元）= 保费规模 × 利润率
const calculateExpectedProfit = (row) => {
  const premiumScale = calculatePremiumScale(row)
  const profitMargin = calculateProfitMargin(row)
  return premiumScale * profitMargin
}

// 情景计算函数
const calculateScenarioPolicyCount = (unit, scenarioId) => {
  const scenario = scenarios.find(s => s.id === scenarioId)
  if (!scenario) return unit.policies
  return Math.round(unit.policies * (1 + scenario.policyAdjust))
}

const calculateScenarioPremium = (unit, scenarioId) => {
  const scenario = scenarios.find(s => s.id === scenarioId)
  if (!scenario) return calculatePremiumScale(unit)
  const scenarioPolicies = calculateScenarioPolicyCount(unit, scenarioId)
  return (scenarioPolicies * unit.avg_premium) / 10000
}

const calculateScenarioProfit = (unit, scenarioId) => {
  const scenario = scenarios.find(s => s.id === scenarioId)
  if (!scenario) return calculateExpectedProfit(unit)

  // 情景下，赔付率会变化，影响边际成本率和利润率
  const params = getEffectiveParams(unit)
  const adjustedLossRatio = (params.target_loss_ratio || 0) * (1 + scenario.profitAdjust)
  const adjustedMarginCostRate = adjustedLossRatio + (params.market_expense_ratio || 0)
  const adjustedProfitMargin = 1 - adjustedMarginCostRate - (params.fixed_cost_ratio || 0)

  const scenarioPremium = calculateScenarioPremium(unit, scenarioId)
  return scenarioPremium * adjustedProfitMargin
}

const calculateScenarioMargin = (unit, scenarioId) => {
  const scenario = scenarios.find(s => s.id === scenarioId)
  if (!scenario) return 0
  const profit = calculateScenarioProfit(unit, scenarioId)
  const premium = calculateScenarioPremium(unit, scenarioId)
  if (premium === 0) return 0
  return profit / premium
}

// 计算单行数据
const calculateRow = (unit) => {
  // 纯风险成本使用预设值，不重新计算
  // unit.pure_risk_cost 已经在 syncBusinessUnitParams 中设置

  // 计算预期利润率
  unit.expected_profit_margin = calculateProfitMargin(unit)
}

const syncBusinessUnitParams = () => {
  const selectedIds = new Set(selectedUnits.value.map(u => u.unit_id))
  businessUnitParams.value = businessUnitParams.value.filter(p => selectedIds.has(p.unit_id))
  selectedUnits.value.forEach(unit => {
    if (!businessUnitParams.value.some(p => p.unit_id === unit.unit_id)) {
      const param = {
        unit_id: unit.unit_id,
        unit_name: unit.unit_name,
        use_global: false,
        fixed_cost_ratio: defaultGlobalParams.fixed_cost_ratio,
        target_loss_ratio: unit.target_loss_ratio || defaultGlobalParams.target_loss_ratio,  // 使用预设赔付率
        market_expense_ratio: defaultGlobalParams.market_expense_ratio,
        autonomous_discount_min: defaultGlobalParams.autonomous_discount_min,
        autonomous_discount_max: defaultGlobalParams.autonomous_discount_max,
        is_calculate: defaultGlobalParams.is_calculate,
        policies: unit.policy_count,
        avg_premium: unit.avg_premium,
        premium_scale: unit.premium_scale,
        pure_risk_cost: getUnitPureRiskCost(unit),  // 使用预设值
        expected_profit_margin: unit.expected_profit_margin || 0.05,
        selectedScenario: 'base'
      }
      // 不重新计算，直接使用预设的利润率
      // param.expected_profit_margin = calculateProfitMargin(param)
      businessUnitParams.value.push(param)
    }
  })
  businessUnitParams.value.forEach(param => {
    if (param.use_global) {
      param.fixed_cost_ratio = globalParams.fixed_cost_ratio
      param.target_loss_ratio = globalParams.target_loss_ratio
      param.market_expense_ratio = globalParams.market_expense_ratio
      param.autonomous_discount_min = globalParams.autonomous_discount_min
      param.autonomous_discount_max = globalParams.autonomous_discount_max
      param.is_calculate = globalParams.is_calculate
    }
    // 初始化完成后，用户修改参数时才重新计算利润率
    if (isInitialized.value) {
      calculateRow(param)
    }
  })
}

// 标志位：是否已初始化完成
const isInitialized = ref(false)

watch(selectedUnits, syncBusinessUnitParams, { deep: true })
watch(globalParams, syncBusinessUnitParams, { deep: true })

const totalPolicies = computed(() => selectedUnits.value.reduce((s, b) => s + b.policy_count, 0))
const totalPremium = computed(() => selectedUnits.value.reduce((s, b) => s + b.premium_scale, 0))
const totalPureRiskCost = computed(() => {
  let total = 0
  businessUnitParams.value.forEach(row => {
    total += (row.policies * (row.pure_risk_cost || 0)) / 10000
  })
  return total
})
const avgProfitMargin = computed(() => {
  if (!selectedUnits.value.length) return 0
  const total = selectedUnits.value.reduce((s, b) => s + b.premium_scale, 0)
  return total ? (selectedUnits.value.reduce((s, b) => s + b.expected_profit_margin * b.premium_scale, 0) / total) * 100 : 0
})
const overallRiskLevel = computed(() => {
  const m = avgProfitMargin.value
  return m >= 8 ? '低风险' : m >= 5 ? '中低风险' : m >= 3 ? '中风险' : m >= 0 ? '中高风险' : '高风险'
})
const totalProfit = computed(() => {
  let total = 0
  businessUnitParams.value.forEach(row => {
    total += (row.policies * row.avg_premium / 10000) * row.expected_profit_margin
  })
  return total
})
const profitMargin = computed(() => totalPremium.value ? (totalProfit.value / (totalPremium.value / 10000)) * 100 : 0)
const allSelected = computed(() => selectedUnits.value.length === allBusinessUnits.value.length)
const hasExpandedScenario = computed(() => scenarioExpanded.value.some(expanded => expanded))

const isSelected = (unit) => selectedUnits.value.some(u => u.unit_id === unit.unit_id)
const toggleSelection = (unit) => {
  const idx = selectedUnits.value.findIndex(u => u.unit_id === unit.unit_id)
  idx > -1 ? selectedUnits.value.splice(idx, 1) : selectedUnits.value.push(unit)
}
const handleSelectAll = () => { selectedUnits.value = allSelected.value ? [] : [...allBusinessUnits.value] }
const getMarginClass = (margin) => {
  if (!margin) return 'low'
  const m = margin * 100
  if (m >= 6) return 'high'
  if (m >= 3) return 'medium'
  if (m >= 0) return 'low'
  return 'negative'
}
const getSuggestionClass = (s) => ({ '推荐': 'recommended', '谨慎': 'cautious', '限制': 'restricted' }[s] || '')
const getRiskClass = (r) => ({ '低风险': 'low', '中低风险': 'medium-low', '中风险': 'medium', '中高风险': 'medium-high', '高风险': 'high' }[r] || '')
const getProfitMarginClass = (m) => m >= 5 ? 'positive-high' : m >= 0 ? 'positive' : 'negative'

const handleUseGlobalChange = (row) => {
  if (row.use_global) {
    // 勾选"兜底" = 使用全局参数
    Object.assign(row, { ...globalParams, use_global: true })
  } else {
    // 不勾选 = 使用独立参数（保持当前值）
    row.use_global = false
  }
  calculateRow(row)
}
const resetToGlobal = (row) => {
  Object.assign(row, { ...globalParams, use_global: true })
  calculateRow(row)
  ElMessage.success('已重置为全局参数')
}
const handleUnitParamChange = (row) => {
  row.use_global = false
  calculateRow(row)
}
const openUnitEditDialog = (row) => {
  currentUnit.value = { ...row }
  editDialogVisible.value = true
}
const saveUnitParams = () => {
  const index = businessUnitParams.value.findIndex(u => u.unit_id === currentUnit.value.unit_id)
  if (index !== -1) {
    businessUnitParams.value[index] = {
      ...businessUnitParams.value[index],
      fixed_cost_ratio: currentUnit.value.fixed_cost_ratio,
      target_loss_ratio: currentUnit.value.target_loss_ratio,
      market_expense_ratio: currentUnit.value.market_expense_ratio,
      autonomous_discount_min: currentUnit.value.autonomous_discount_min,
      autonomous_discount_max: currentUnit.value.autonomous_discount_max,
      is_calculate: currentUnit.value.is_calculate,
      use_global: false
    }
    calculateRow(businessUnitParams.value[index])
  }
  editDialogVisible.value = false
  ElMessage.success('参数已保存并重新测算')
}
const toggleScenario = (i) => { scenarioExpanded.value[i] = !scenarioExpanded.value[i] }

const selectScenario = (unit, scenarioId) => {
  unit.selectedScenario = scenarioId
}

const applyScenario = (unit, scenarioId) => {
  const scenario = scenarios.find(s => s.id === scenarioId || s.id === unit.selectedScenario)
  if (scenario) {
    const targetScenarioId = scenarioId || unit.selectedScenario
    unit.selectedScenario = targetScenarioId
    unit.policies = calculateScenarioPolicyCount(unit, targetScenarioId)
    unit.expected_profit_margin = calculateScenarioMargin(unit, targetScenarioId)
    ElMessage.success(`已应用${scenario.name}`)
  }
}

// 批量测算
const calculateAll = () => {
  businessUnitParams.value.forEach(row => {
    calculateRow(row)
  })
  ElMessage.success('批量测算完成')
}


const overallCalculate = () => {
  businessUnitParams.value.forEach(row => {
    calculateRow(row)
  })
  ElMessage.success('整体测算完成')
}

const nextStep = () => {
  if (currentStep.value === 0 && (!formData.name || !formData.institutions.length)) {
    ElMessage.warning('请输入策略名称并选择生效机构')
    return
  }
  if (currentStep.value === 1) syncBusinessUnitParams()
  if (currentStep.value < 4) currentStep.value++
}

const prevStep = () => { if (currentStep.value > 0) currentStep.value-- }

// 加载策略详情（编辑模式）
const loadStrategyForEdit = async () => {
  if (!route.params.id) return
  
  try {
    const response = await getStrategy(route.params.id)
    const data = response.data || response
    
    // 填充基本信息
    formData.name = data.name || ''
    formData.description = data.description || ''
    if (data.institutions?.length) {
      formData.institutions = data.institutions.map(i => i.name || i)
    }
    
    // 填充业务单元
    if (data.business_units?.length) {
      selectedUnits.value = data.business_units.map(bu => ({
        unit_id: bu.unit_id,
        unit_name: bu.unit_name,
        description: bu.description || '',
        policy_count: bu.policies || bu.policy_count || 0,
        avg_premium: parseFloat(bu.avg_premium) || 0,
        premium_scale: (bu.policies || bu.policy_count || 0) * (parseFloat(bu.avg_premium) || 0),
        pure_risk_cost: parseFloat(bu.pure_risk_cost) || 0,
        target_loss_ratio: parseFloat(bu.target_loss_ratio) || 0.75,
        expected_profit_margin: parseFloat(bu.expected_profit_margin) || 0,
        strategy_suggestion: bu.strategy_suggestion || '推荐'
      }))
    }
    
    // 填充成本模拟参数
    if (data.cost_simulation?.global_params) {
      const gp = data.cost_simulation.global_params
      fixedCostRatio.value = parseFloat(gp.fixed_cost_ratio) || 0.10
      targetLossRatio.value = parseFloat(gp.target_loss_ratio) || 0.75
      marketExpenseRatio.value = parseFloat(gp.market_expense_ratio) || 0.12
      autonomousDiscountMin.value = parseFloat(gp.autonomous_discount_min) || 0.70
      autonomousDiscountMax.value = parseFloat(gp.autonomous_discount_max) || 1.30
      isCalculate.value = gp.is_calculate ?? true
    }
    
    ElMessage.success('策略信息已加载')
  } catch (error) {
    console.error('加载策略失败:', error)
    ElMessage.error('加载策略失败：' + error.message)
  }
}

// 确保全局参数正确初始化
onMounted(async () => {
  console.log('globalParams 初始化:', globalParams)
  // 确保值是数字类型
  globalParams.fixed_cost_ratio = 0.10
  globalParams.target_loss_ratio = 0.75
  globalParams.market_expense_ratio = 0.12
  globalParams.autonomous_discount_min = 0.70
  globalParams.autonomous_discount_max = 1.30
  globalParams.is_calculate = true
  
  // 加载业务单元数据（从数据库读取）
  await loadBusinessUnits()
  
  // 如果是编辑模式，加载策略详情
  if (route.params.id) {
    await loadStrategyForEdit()
  }
  
  // 标记初始化完成
  isInitialized.value = true
})

const reset = () => { formData.name = ''; formData.description = ''; formData.institutions = [] }

const confirmSave = async () => {
  try {
    let strategyId = route.params.id
    let isNewStrategy = false

    if (!strategyId) {
      const strategyData = {
        name: formData.name,
        description: formData.description,
        institutions: formData.institutions.map(n => ({ code: n.toLowerCase(), name: n }))
      }
      const createResult = await createStrategy(strategyData)
      strategyId = createResult.data.id
      isNewStrategy = true
      ElMessage.info('策略创建成功，继续保存向导数据...')
    }

    const selectedBusinessUnits = selectedUnits.value.map(unit => ({
      id: unit.unit_id,
      name: unit.unit_name
    }))
    await saveWizardBusinessUnit(strategyId, { business_units: selectedBusinessUnits })
    ElMessage.info('业务单元保存成功...')

    const costSimulationData = {
      global_params: { ...globalParams.value },
      business_unit_params: businessUnitParams.value.map(param => ({
        unit_id: param.unit_id,
        unit_name: param.unit_name,
        fixed_cost_ratio: param.fixed_cost_ratio,
        target_loss_ratio: param.target_loss_ratio,
        market_expense_ratio: param.market_expense_ratio,
        autonomous_discount_min: param.autonomous_discount_min,
        autonomous_discount_max: param.autonomous_discount_max,
        is_calculate: param.is_calculate
      }))
    }
    await saveWizardCostSimulation(strategyId, costSimulationData)
    ElMessage.info('成本模拟保存成功...')

    const revenueSimulationData = {
      simulation_scope: 'all',
      adjusted_params: null
    }
    await saveWizardRevenueSimulation(strategyId, revenueSimulationData)
    ElMessage.info('收益模拟保存成功...')

    const confirmResult = await confirmWizard(strategyId)
    ElMessage.success('策略保存成功！状态已更新为 simulation_passed')

    router.push('/admin/strategy/overview')
  } catch (e) {
    console.error('保存策略失败:', e)
    ElMessage.error('保存失败：' + (e.message || e.response?.data?.detail || '未知错误'))
  }
}
</script>

<style scoped>
/* 页面整体 */
.strategy-wizard-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 4px 0;
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
}

.page-description {
  margin: 0;
  font-size: 13px;
  color: #666;
}

/* 步骤卡片 */
.steps-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.steps-card :deep(.el-card__body) {
  padding: 24px 32px;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e4e7ed;
  color: #606266;
  font-weight: 600;
  font-size: 14px;
}

.step-number-active {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.steps-card :deep(.el-step__title) {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.steps-card :deep(.el-step__description) {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 内容卡片 */
.content-card {
  border-radius: 8px;
  min-height: 500px;
}

.content-card :deep(.el-card__body) {
  padding: 24px;
}

/* 步骤面板 */
.step-panel {
  min-height: 400px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.panel-header .el-icon {
  font-size: 20px;
  color: #667eea;
}

.panel-subtitle {
  font-size: 13px;
  color: #909399;
  margin-left: 8px;
}

/* 表单样式 */
.basic-form {
  max-width: 600px;
}

.form-input-large {
  max-width: 400px;
}

/* 问题 1：生效机构布局 - flex 布局，一行显示 */
.institution-row {
  display: flex !important;
  flex-wrap: nowrap !important;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
  width: 100% !important;
}

.institution-row :deep(.el-checkbox-group) {
  display: flex !important;
  flex-wrap: nowrap !important;
  gap: 12px;
  width: 100% !important;
}

.institution-checkbox-inline {
  flex-shrink: 0 !important;
  width: auto !important;
  min-width: 100px !important;
  margin-right: 0 !important;
}

/* 滚动条样式优化 */
.institution-row::-webkit-scrollbar {
  height: 6px;
}

.institution-row::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.institution-row::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.institution-row::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 问题 2：移除所有数字输入框的上下箭头 - 增强版 */
:deep(input[type="number"]) {
  -moz-appearance: textfield !important;
}

:deep(input[type="number"]::-webkit-outer-spin-button),
:deep(input[type="number"]::-webkit-inner-spin-button) {
  -webkit-appearance: none !important;
  margin: 0 !important;
  display: none !important;
}

/* Element Plus 数字输入框的增减按钮 */
:deep(.el-input-number__decrease),
:deep(.el-input-number__increase) {
  display: none !important;
}

/* 区域标题 */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 20px 0 12px 0;
}

.section-title h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.section-title .el-icon {
  font-size: 18px;
  color: #667eea;
}

/* 问题 4：带按钮的区域标题 */
.section-title-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0 12px 0;
}

.section-title-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title-left h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

/* 工具栏 */
.section-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar-left h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th {
  background: #fafafa;
  color: #606266;
  font-weight: 600;
  padding: 12px 8px;
  border: 1px solid #ebeef5;
  text-align: left;
  font-size: 13px;
}

.data-table td {
  padding: 12px 8px;
  border: 1px solid #ebeef5;
}

.table-row:hover {
  background: #f5f7fa;
}

.table-row.selected {
  background: #ecf5ff;
}

.text-center { text-align: center; }
.text-right { text-align: right; }

.number {
  font-family: 'Segoe UI', Arial, sans-serif;
  font-weight: 600;
  color: #303133;
}

.unit-id { font-family: monospace; color: #666; }
.unit-name { font-weight: 600; color: #303133; }
.unit-desc { color: #909399; }

/* 徽章样式 */
.margin-badge, .suggestion-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.margin-badge.high { background: #f0f9ff; color: #409EFF; }
.margin-badge.medium-high { background: #f0f9ff; color: #67c23a; }
.margin-badge.medium { background: #fdf6ec; color: #e6a23c; }
.margin-badge.negative { background: #fef0f0; color: #f56c6c; }

.suggestion-badge.recommended { background: #f0f9ff; color: #409EFF; }
.suggestion-badge.cautious { background: #fdf6ec; color: #e6a23c; }
.suggestion-badge.restricted { background: #fef0f0; color: #f56c6c; }

/* 汇总卡片 */
.summary-section {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.summary-card-stat {
  background: white;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.policies { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.premium { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-icon.margin { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-icon.risk { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
.stat-icon.risk.low { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.risk.medium-low { background: linear-gradient(135deg, #67c23a 0%, #36c692 100%); }
.stat-icon.risk.medium { background: linear-gradient(135deg, #e6a23c 0%, #f56c6c 100%); }
.stat-icon.risk.medium-high, .stat-icon.risk.high { background: linear-gradient(135deg, #f56c6c 0%, #c0392b 100%); }

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}

.stat-unit {
  font-size: 12px;
  color: #909399;
  font-weight: 400;
  margin-left: 2px;
}

/* 参数卡片 */
.global-params-card, .unit-params-card {
  border-radius: 8px;
}

.params-form {
  width: 100%;
}

/* 全局参数输入框 - 统一宽度 */
.params-form .el-form-item {
  margin-right: 24px;
}

.params-form .el-input-number {
  width: 100px !important;
}

.params-form .el-input-number :deep(.el-input__wrapper) {
  width: 100px !important;
}

.params-form .el-input-number :deep(input) {
  text-align: center !important;
  color: #303133 !important;
  font-size: 13px !important;
}

/* 汇总指标卡片 */
.summary-metrics-card {
  border-radius: 8px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
}

.metric-item {
  padding: 20px;
  background: white;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.metric-item.primary { border-top: 3px solid #667eea; }
.metric-item.success { border-top: 3px solid #67c23a; }
.metric-item.warning { border-top: 3px solid #e6a23c; }
.metric-item.info { border-top: 3px solid #409EFF; }

.metric-icon {
  font-size: 28px;
  margin-bottom: 10px;
  color: #667eea;
}

.metric-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.metric-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.metric-unit {
  font-size: 14px;
  color: #909399;
  font-weight: 400;
  margin-left: 2px;
}

.positive { color: #67c23a; }
.positive-high { color: #36c692; }
.negative { color: #f56c6c; }

/* 详情卡片 */
.detail-card {
  border-radius: 8px;
}

.card-header-with-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header-with-actions span {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
}

/* 情景展开 */
.scenario-toggle {
  text-align: center;
}

/* 表格展开行内容 */
.scenario-expand-content {
  background: #fafafa;
  padding: 20px;
  margin: -1px; /* 抵消表格边框 */
}

/* 情景卡片网格 - 5 列横向 */
.scenario-cards-grid-simple {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.scenario-card-simple {
  background: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  transition: all 0.2s;
}

.scenario-card-simple.active {
  border-color: #409EFF;
  background: #ecf5ff;
}

.scenario-card-header-simple {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #f0f0f0;
}

.scenario-name-simple {
  font-size: 12px;
  font-weight: 600;
  color: #303133;
}

.scenario-metrics-simple {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
}

.metric-simple {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.metric-label-simple {
  color: #909399;
}

.metric-value-simple {
  font-weight: 600;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 12px;
}

.scenario-apply-btn {
  width: 100%;
}

.scenario-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 2px solid #e4e7ed;
  transition: all 0.2s;
}

.scenario-card.active {
  border-color: #409EFF;
  background: #ecf5ff;
}

.scenario-card-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  text-align: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.scenario-metrics {
  margin: 12px 0;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  font-size: 13px;
}

.metric-label {
  color: #909399;
}

.metric-value {
  font-weight: 600;
  color: #303133;
  font-size: 13px;
}

.scenario-card-action {
  text-align: center;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}



/* 策略摘要卡片 */
.strategy-summary-card {
  border-radius: 8px;
}

.params-subsection-compact {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.params-subsection-compact h4 {
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.desc-label-small {
  font-weight: 600;
  color: #606266;
  width: 90px;
  font-size: 12px;
}

.desc-value-small {
  font-weight: 600;
  color: #303133;
  font-size: 12px;
}

.text-muted {
  color: #909399;
  font-size: 12px;
}

/* 业务单元汇总卡片 */
.business-units-summary-card {
  border-radius: 8px;
}

/* 问题 6：整体合计区域 - 白色卡片，移到最后 */
.overall-totals-white {
  margin-top: 20px;
  padding: 20px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.totals-title-black {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.totals-title-black h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.totals-grid {
  text-align: center;
}

.total-item {
  padding: 12px;
}

.total-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.total-value {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}

.total-unit {
  font-size: 13px;
  color: #909399;
  font-weight: 400;
  margin-left: 2px;
}

.total-value.positive { color: #67c23a; }

/* 贡献度分析 */
.contribution-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.contribution-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.contribution-bar {
  width: 100%;
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.contribution-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.3s;
}

/* 固定底部操作区 */
.fixed-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e4e7ed;
}

.fixed-actions .el-button {
  min-width: 120px;
}

/* 编辑弹窗样式 */
.range-form-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.range-text {
  color: #909399;
}

.dialog-unit-name {
  font-weight: 600;
  color: #303133;
}

/* 辅助类 */
.mb-4 { margin-bottom: 16px; }
.mt-4 { margin-top: 16px; }
.ml-1 { margin-left: 4px; }
</style>
