<template>
  <div class="result-page">
    <div class="page-header">
      <h1>🎯 智能决策结果</h1>
      <p>基于策略引擎的实时推荐 — 车险场景示例</p>
    </div>

    <!-- 推荐报价卡片 -->
    <el-card class="recommend-card" shadow="hover">
      <template #header>
        <div class="recommend-header">
          <el-tag type="warning" effect="dark">
            <el-icon><Star /></el-icon>
            强烈推荐
          </el-tag>
          <h2>最优报价方案</h2>
        </div>
      </template>

      <div class="recommend-content">
        <div class="insurer-info">
          <div class="insurer-logo">
            <el-icon :size="40"><OfficeBuilding /></el-icon>
          </div>
          <div class="insurer-detail">
            <h3>{{ recommendedQuote.insurerName }}</h3>
            <p class="premium">
              <span class="label">总保费：</span>
              <span class="amount">¥{{ recommendedQuote.totalPremium.toFixed(2) }}</span>
            </p>
            <el-rate v-model="recommendedQuote.rating" disabled show-score text-color="#ff9900" size="small" />
          </div>
        </div>

        <!-- 精简评分维度 -->
        <div class="score-grid">
          <div class="score-item-compact">
            <div class="score-label">💰 价格</div>
            <el-progress :percentage="recommendedQuote.scores.price" :stroke-width="12" :show-text="false" />
            <div class="score-text">{{ recommendedQuote.scores.price }}分</div>
          </div>
          <div class="score-item-compact">
            <div class="score-label">⭐ 服务</div>
            <el-progress :percentage="recommendedQuote.scores.service" :stroke-width="12" :show-text="false" />
            <div class="score-text">{{ recommendedQuote.scores.service }}分</div>
          </div>
          <div class="score-item-compact">
            <div class="score-label">⚡ 赔付</div>
            <el-progress :percentage="recommendedQuote.scores.claim" :stroke-width="12" :show-text="false" />
            <div class="score-text">{{ recommendedQuote.scores.claim }}分</div>
          </div>
        </div>

        <!-- 精简推荐理由 -->
        <div class="recommend-reason-compact">
          <h4>🤖 AI 推荐理由</h4>
          <div class="reason-tags">
            <el-tag v-for="(reason, index) in recommendedQuote.reasons" :key="index" size="small" effect="plain">
              {{ reason }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 精简对比表格 -->
    <el-card class="comparison-card" shadow="hover" style="margin-top: 16px">
      <template #header>
        <h3>📊 保司对比</h3>
      </template>

      <el-table :data="allQuotes" stripe size="small" style="width: 100%">
        <el-table-column type="index" label="排名" width="60" align="center" />
        <el-table-column label="保司名称" min-width="150">
          <template #default="{ row }">
            <div class="insurer-name">
              <el-icon v-if="row.isRecommended" color="#f7ba2a"><Star /></el-icon>
              <span>{{ row.insurerName }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="总保费" width="120" align="right">
          <template #default="{ row }">
            <span :class="{ 'highlight-price': row.isRecommended }">
              ¥{{ row.totalPremium.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="交强险" width="100" align="right">
          <template #default="{ row }">
            ¥{{ row.premiums.compulsory?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column label="商业险" width="100" align="right">
          <template #default="{ row }">
            ¥{{ row.premiums.commercial?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column label="综合评分" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getScoreTagType(row.overallScore)">
              {{ row.overallScore }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              :type="row.isRecommended ? 'primary' : ''"
              size="small"
              @click="handleSelect(row)"
            >
              {{ row.isRecommended ? '选择方案' : '选择' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 操作按钮 -->
    <div class="form-actions" style="margin-top: 16px">
      <el-button type="primary" size="large" @click="handleConfirm">
        <el-icon><Check /></el-icon>
        确认投保
      </el-button>
      <el-button size="large" @click="handleRequote">
        <el-icon><Refresh /></el-icon>
        重新询价
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Star,
  OfficeBuilding,
  Check,
  Refresh
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 从 sessionStorage 加载报价结果
const quoteResult = JSON.parse(sessionStorage.getItem('quoteResult') || '{}')

// 推荐报价数据
const recommendedQuote = reactive({
  insurerName: quoteResult.recommended_quote?.insurer_name || '人保财险',
  totalPremium: quoteResult.recommended_quote?.premiums?.total || 4580.00,
  rating: (quoteResult.recommended_quote?.scores?.overall || 95) / 10,
  scores: {
    price: quoteResult.recommended_quote?.scores?.price || 92,
    service: quoteResult.recommended_quote?.scores?.service || 95,
    claim: quoteResult.recommended_quote?.scores?.claim || 88
  },
  reasons: quoteResult.recommended_quote?.reasons || [
    '价格竞争力强，低于市场均价 8%',
    '服务质量优秀，客户满意度 95%',
    '赔付效率高，平均赔付周期 3.5 天',
    '品牌信誉好，市场占有率第一'
  ]
})

// 所有报价数据
const allQuotes = ref(
  (quoteResult.quotes || []).map((quote, index) => ({
    rank: index + 1,
    insurerName: quote.insurer_name,
    totalPremium: quote.premiums.total,
    premiums: quote.premiums,
    overallScore: quote.scores.overall,
    isRecommended: quote.is_recommended
  }))
)

// 获取评分颜色
const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
}

// 获取评分标签类型
const getScoreTagType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'primary'
  if (score >= 70) return 'warning'
  return 'danger'
}

// 选择方案
const handleSelect = (quote) => {
  ElMessage.success(`已选择 ${quote.insurerName} 方案`)
}

// 确认投保
const handleConfirm = () => {
  ElMessage.success('投保确认成功，将跳转至支付页面')
  // TODO: 跳转至支付页面
}

// 重新询价
const handleRequote = () => {
  router.push('/quote')
}
</script>

<style scoped>
.result-page {
  padding: 16px;
  min-height: 100vh;
  background-color: #f5f7fa;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 16px;
  text-align: center;
}

.page-header h1 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.page-header p {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.recommend-card {
  max-width: 900px;
}

.recommend-content {
  padding: 8px 0;
}

.insurer-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.insurer-logo {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 8px;
}

.insurer-detail h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
}

.premium {
  font-size: 14px;
  color: #606266;
  margin: 0 0 8px 0;
}

.premium .label {
  color: #909399;
}

.premium .amount {
  font-size: 20px;
  font-weight: 600;
  color: #f56c6c;
  margin-left: 8px;
}

/* 精简评分网格 */
.score-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.score-item-compact {
  text-align: center;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
}

.score-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
  font-weight: 500;
}

.score-text {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 精简推荐理由 */
.recommend-reason-compact {
  margin-top: 12px;
}

.recommend-reason-compact h4 {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
}

.reason-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.reason-tags .el-tag {
  font-size: 12px;
  padding: 4px 10px;
}

.recommend-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.recommend-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.recommend-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.insurer-info {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.insurer-logo {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fff;
  border-radius: 8px;
  color: #409eff;
  flex-shrink: 0;
}

.insurer-detail h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.insurer-detail .premium {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.insurer-detail .premium .label {
  color: #606266;
}

.insurer-detail .premium .amount {
  font-size: 24px;
  font-weight: 700;
  color: #f56c6c;
  margin-left: 8px;
}

.score-breakdown h4,
.recommend-reason h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.score-item {
  margin-bottom: 14px;
}

.score-item:last-child {
  margin-bottom: 0;
}

.score-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 14px;
}

.score-label .score-value {
  font-weight: 600;
  color: #409eff;
}

.recommend-reason ul {
  margin: 0;
  padding-left: 20px;
}

.recommend-reason li {
  margin-bottom: 6px;
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}

.comparison-card {
  max-width: 900px;
}

.comparison-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.insurer-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.highlight-price {
  font-weight: 700;
  color: #f56c6c;
  font-size: 16px;
}

.process-card {
  max-width: 900px;
}

.process-card h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.form-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 32px;
  padding: 24px;
  background-color: #fff;
  border-radius: 4px;
  max-width: 900px;
}
</style>
