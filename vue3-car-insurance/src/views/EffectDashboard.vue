<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1>📊 效果看板</h1>
      <p>实时监控策略效果和业务指标</p>
    </div>

    <!-- 核心指标卡片 -->
    <el-row :gutter="20" class="metric-cards">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-indicator indicator-primary"></div>
          <div class="metric-label">保费收入</div>
          <div class="metric-value">¥{{ (metrics.premiumIncome / 10000).toFixed(0) }}万</div>
          <div class="metric-trend trend-up">
            <el-icon><Top /></el-icon>
            <span>较上月 +{{ metrics.premiumGrowth }}%</span>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-indicator indicator-success"></div>
          <div class="metric-label">利润贡献</div>
          <div class="metric-value">¥{{ (metrics.profitContribution / 10000).toFixed(0) }}万</div>
          <div class="metric-trend trend-up">
            <el-icon><Top /></el-icon>
            <span>较上月 +{{ metrics.profitGrowth }}%</span>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-indicator indicator-warning"></div>
          <div class="metric-label">利润率</div>
          <div class="metric-value">{{ metrics.profitMargin.toFixed(1) }}%</div>
          <div class="metric-trend trend-up">
            <el-icon><Top /></el-icon>
            <span>较上月 +{{ metrics.marginGrowth }}%</span>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-indicator indicator-info"></div>
          <div class="metric-label">成交率</div>
          <div class="metric-value">{{ metrics.conversionRate.toFixed(0) }}%</div>
          <div class="metric-trend trend-up">
            <el-icon><Top /></el-icon>
            <span>较上月 +{{ metrics.conversionGrowth }}%</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 保费收入趋势（折线图） -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <h3>保费收入趋势（近 30 天）</h3>
          <el-radio-group v-model="trendPeriod" size="small">
            <el-radio-button label="7d">7 天</el-radio-button>
            <el-radio-button label="15d">15 天</el-radio-button>
            <el-radio-button label="30d">30 天</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div class="chart-container">
        <svg class="line-chart" viewBox="0 0 800 300" preserveAspectRatio="none">
          <!-- 网格线 -->
          <line v-for="i in 5" :key="'grid-'+i" 
            :x1="0" :y1="(i-1) * 75" :x2="800" :y2="(i-1) * 75"
            stroke="#e4e7ed" stroke-width="1" stroke-dasharray="4,4"/>
          
          <!-- 折线 -->
          <polyline
            :points="linePoints"
            fill="none"
            stroke="#409EFF"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          
          <!-- 数据点 -->
          <circle
            v-for="(point, index) in chartPoints"
            :key="'point-'+index"
            :cx="point.x"
            :cy="point.y"
            r="5"
            fill="#409EFF"
            stroke="#fff"
            stroke-width="2"
            class="chart-point"
          />
          
          <!-- X 轴标签 -->
          <text
            v-for="(day, index) in trendData"
            :key="'label-'+index"
            :x="index * (800 / (trendData.length - 1))"
            y="295"
            text-anchor="middle"
            font-size="11"
            fill="#909399"
          >
            {{ day.label }}
          </text>
        </svg>
      </div>
    </el-card>

    <!-- 业务单元分布 -->
    <el-card class="table-card">
      <template #header>
        <h3>业务单元分布</h3>
      </template>
      <el-table :data="businessUnits" stripe style="width: 100%" :cell-style="{padding: '12px 8px'}">
        <el-table-column prop="unit_name" label="业务单元" min-width="180" />
        <el-table-column prop="premium_income" label="保费收入" width="130" align="right">
          <template #default="{ row }">
            <span class="currency-value">¥{{ (row.premium_income / 10000).toFixed(0) }}万</span>
          </template>
        </el-table-column>
        <el-table-column prop="percentage" label="占比" width="150" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.percentage" :color="getPercentageColor(row.percentage)" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="profit_contribution" label="利润贡献" width="130" align="right">
          <template #default="{ row }">
            <span :class="row.profit_contribution >= 0 ? 'profit-positive' : 'profit-negative'">
              {{ row.profit_contribution >= 0 ? '+' : '' }}¥{{ (row.profit_contribution / 10000).toFixed(0) }}万
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_margin" label="利润率" width="120" align="center">
          <template #default="{ row }">
            <span :class="row.profit_margin >= 0.05 ? 'profit-high' : row.profit_margin < 0 ? 'profit-negative' : 'profit-low'">
              {{ (row.profit_margin * 100).toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 策略对比 -->
    <el-card class="strategy-card">
      <template #header>
        <h3>策略效果对比</h3>
      </template>
      <el-table :data="strategies" stripe style="width: 100%" :cell-style="{padding: '12px 8px'}">
        <el-table-column prop="strategy_name" label="策略名称" min-width="200" />
        <el-table-column prop="premium_income" label="保费收入" width="130" align="right">
          <template #default="{ row }">
            <span class="currency-value">¥{{ (row.premium_income / 10000).toFixed(0) }}万</span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_contribution" label="利润贡献" width="130" align="right">
          <template #default="{ row }">
            <span class="currency-value">¥{{ (row.profit_contribution / 10000).toFixed(0) }}万</span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_margin" label="利润率" width="100" align="center">
          <template #default="{ row }">
            <span class="percentage-value">{{ (row.profit_margin * 100).toFixed(1) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="conversion_rate" label="成交率" width="100" align="center">
          <template #default="{ row }">
            <span class="percentage-value">{{ (row.conversion_rate * 100).toFixed(1) }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="最优指标" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_best" type="success" size="small" effect="plain">🏆 最优</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Top } from '@element-plus/icons-vue'

// 趋势周期
const trendPeriod = ref('30d')

// 核心指标
const metrics = reactive({
  premiumIncome: 25760000,
  premiumGrowth: 12,
  profitContribution: 850000,
  profitGrowth: 25,
  profitMargin: 3.3,
  marginGrowth: 8,
  conversionRate: 46,
  conversionGrowth: 5
})

// 趋势数据
const trendData = reactive([
  { label: '3/1', value: 800000 },
  { label: '3/2', value: 850000 },
  { label: '3/3', value: 900000 },
  { label: '3/4', value: 880000 },
  { label: '3/5', value: 920000 },
  { label: '3/6', value: 950000 },
  { label: '3/7', value: 870000 },
  { label: '3/8', value: 900000 },
  { label: '3/9', value: 930000 },
  { label: '3/10', value: 960000 },
  { label: '3/11', value: 940000 },
  { label: '3/12', value: 980000 },
  { label: '3/13', value: 910000 },
  { label: '3/14', value: 950000 },
  { label: '3/15', value: 990000 },
  { label: '3/16', value: 1020000 },
  { label: '3/17', value: 1000000 },
  { label: '3/18', value: 1050000 },
  { label: '3/19', value: 1080000 },
  { label: '3/20', value: 1000000 },
  { label: '3/21', value: 1030000 },
  { label: '3/22', value: 1070000 },
  { label: '3/23', value: 1100000 },
  { label: '3/24', value: 1080000 },
  { label: '3/25', value: 1120000 },
  { label: '3/26', value: 1150000 },
  { label: '3/27', value: 1100000 },
  { label: '3/28', value: 1130000 },
  { label: '3/29', value: 1160000 },
  { label: '3/30', value: 1200000 }
])

const maxDayValue = Math.max(...trendData.map(d => d.value))
const minDayValue = Math.min(...trendData.map(d => d.value))

// 计算折线图数据点
const chartPoints = computed(() => {
  const padding = 40
  const chartWidth = 800 - padding * 2
  const chartHeight = 250
  
  return trendData.map((day, index) => {
    const x = padding + (index * chartWidth / (trendData.length - 1))
    const y = chartHeight - ((day.value - minDayValue) / (maxDayValue - minDayValue) * chartHeight)
    return { x, y, value: day.value }
  })
})

// 计算折线图的点字符串
const linePoints = computed(() => {
  return chartPoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

// 业务单元数据
const businessUnits = reactive([
  { unit_name: '燃油车 - 续保客户', premium_income: 9450000, percentage: 37, profit_contribution: 570000, profit_margin: 0.06 },
  { unit_name: '燃油车 - 新保客户', premium_income: 3360000, percentage: 17, profit_contribution: 100000, profit_margin: 0.03 },
  { unit_name: '新能源 - 高价值客户', premium_income: 3650000, percentage: 15, profit_contribution: 110000, profit_margin: 0.03 },
  { unit_name: '新能源 - 普通客户', premium_income: 5400000, percentage: 24, profit_contribution: -160000, profit_margin: -0.03 },
  { unit_name: '豪车 - 续保客户', premium_income: 3900000, percentage: 13, profit_contribution: 230000, profit_margin: 0.06 }
])

// 策略对比数据
const strategies = reactive([
  { strategy_name: '燃油车续保专属策略', premium_income: 9450000, profit_contribution: 570000, profit_margin: 0.06, conversion_rate: 0.54, is_best: true },
  { strategy_name: '新能源高价值策略', premium_income: 3650000, profit_contribution: 110000, profit_margin: 0.03, conversion_rate: 0.42, is_best: false },
  { strategy_name: '豪车续保优质策略', premium_income: 3900000, profit_contribution: 230000, profit_margin: 0.06, conversion_rate: 0.52, is_best: false }
])

// 获取百分比颜色
const getPercentageColor = (percentage) => {
  if (percentage >= 30) return '#67c23a'
  if (percentage >= 20) return '#409eff'
  if (percentage >= 10) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
.dashboard-page {
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

.metric-cards {
  margin-bottom: 20px;
}

/* 核心指标卡片 - 商业风格 */
.metric-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

.metric-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* 顶部彩色指示条 */
.metric-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.indicator-primary {
  background: linear-gradient(90deg, #409EFF 0%, #66b1ff 100%);
}

.indicator-success {
  background: linear-gradient(90deg, #67c23a 0%, #85ce61 100%);
}

.indicator-warning {
  background: linear-gradient(90deg, #e6a23c 0%, #ebb563 100%);
}

.indicator-info {
  background: linear-gradient(90deg, #909399 0%, #a6a9ad 100%);
}

.metric-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
  font-weight: 500;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #67c23a;
}

.trend-up {
  color: #67c23a;
}

.trend-down {
  color: #f56c6c;
}

/* 卡片通用样式 */
.chart-card, .table-card, .strategy-card {
  margin-bottom: 20px;
  border: none;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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

/* 折线图样式 */
.chart-container {
  height: 300px;
  padding: 20px 0;
}

.line-chart {
  width: 100%;
  height: 100%;
}

.chart-point {
  transition: all 0.3s;
  cursor: pointer;
}

.chart-point:hover {
  r: 7;
  fill: #66b1ff;
}

/* 表格样式优化 */
:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
  font-size: 13px;
}

:deep(.el-table td) {
  padding: 12px 8px;
}

.currency-value {
  font-family: 'Segoe UI', Arial, sans-serif;
  font-weight: 600;
  color: #303133;
}

.percentage-value {
  font-weight: 600;
  color: #303133;
}

.profit-positive {
  color: #67c23a;
  font-weight: 600;
}

.profit-negative {
  color: #f56c6c;
  font-weight: 600;
}

.profit-high {
  color: #67c23a;
  font-weight: 600;
}

.profit-low {
  color: #e6a23c;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 1200px) {
  .metric-cards .el-col {
    span: 12;
  }
}

@media (max-width: 768px) {
  .metric-cards .el-col {
    span: 24;
  }
}
</style>
