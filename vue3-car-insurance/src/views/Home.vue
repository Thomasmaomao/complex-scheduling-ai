<template>
  <div class="home-page">
    <!-- 顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-content">
        <div class="logo">
          <span class="logo-icon">🧠</span>
          <h1>智能业务决策平台</h1>
          <span class="version">Beta v1.0</span>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- 左侧：品牌展示 + 适用场景 -->
        <div class="left-column">
          <div class="hero-card">
            <h1 class="hero-title">智能业务决策平台</h1>
            <p class="hero-subtitle">基于数据驱动的业务决策平台，支持多维度业务核算、成本收益分析、策略效果预估和持续优化</p>
          </div>
          <div class="scenarios-bar">
            <div class="scenario-tag">
              <span class="scenario-icon">💰</span>
              <div class="tag-title">金融科技</div>
              <div class="tag-desc">信贷定价、风控策略</div>
            </div>
            <div class="scenario-tag">
              <span class="scenario-icon">💻</span>
              <div class="tag-title">SaaS 服务</div>
              <div class="tag-desc">订阅定价、套餐设计</div>
            </div>
            <div class="scenario-tag">
              <span class="scenario-icon">🛡️</span>
              <div class="tag-title">保险科技</div>
              <div class="tag-desc">精算定价、承保策略</div>
            </div>
          </div>
        </div>

        <!-- 右侧：两个入口卡片 -->
        <div class="right-column">
          <div class="entry-card customer" @click="goToQuote">
            <div class="card-header">
              <div class="entry-icon">💁</div>
              <h3>智能服务</h3>
              <p class="entry-subtitle">Smart Service — 面向 C 端/A 端用户的实时决策服务</p>
            </div>
            <div class="card-body">
              <ul class="feature-list">
                <li><span class="check-icon">✓</span> 快速业务决策</li>
                <li><span class="check-icon">✓</span> 智能方案推荐</li>
                <li><span class="check-icon">✓</span> 多维度对比</li>
                <li><span class="check-icon">✓</span> AI 可解释性</li>
              </ul>
            </div>
            <div class="card-footer">
              <button class="action-button primary">开始使用</button>
            </div>
          </div>

          <div class="entry-card admin" @click="goToAdmin">
            <div class="card-header">
              <div class="entry-icon">⚙️</div>
              <h3>策略中心</h3>
              <p class="entry-subtitle">Strategy Center — 面向 B 端管理者的策略配置与优化平台</p>
            </div>
            <div class="card-body">
              <ul class="feature-list">
                <li><span class="check-icon">✓</span> 策略配置中心</li>
                <li><span class="check-icon">✓</span> 策略测试中心</li>
                <li><span class="check-icon">✓</span> 发布与效果分析</li>
                <li><span class="check-icon">✓</span> 渠道管理</li>
              </ul>
            </div>
            <div class="card-footer">
              <button class="action-button secondary">进入管理</button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToQuote = () => {
  router.push('/quote')
}

const goToAdmin = () => {
  router.push('/admin')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 顶部导航栏 - 减小高度 */
.top-nav {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 12px 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 28px;
}

.logo h1 {
  font-size: 20px;
  color: white;
  margin: 0;
  font-weight: 600;
}

.version {
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  background: rgba(255, 255, 255, 0.2);
  padding: 3px 8px;
  border-radius: 10px;
  margin-left: 8px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 40px;
  background: #f8fafc;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 24px;
  align-items: stretch;
}

/* 左侧列 - 2:1 高度比 */
.left-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

/* 品牌卡片 - 占 2/3 高度 */
.hero-card {
  flex: 2;
  min-height: 380px;
  background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 50%, #a78bfa 100%);
  border-radius: 20px;
  padding: 50px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: white;
  box-shadow: 0 10px 40px rgba(124, 58, 237, 0.3);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.hero-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  pointer-events: none;
}

.hero-card .hero-title {
  font-size: 38px;
  font-weight: 700;
  margin: 0 0 18px 0;
  letter-spacing: 1px;
  text-shadow: 0 3px 15px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 1;
}

.hero-card .hero-subtitle {
  font-size: 15px;
  line-height: 2;
  margin: 0;
  opacity: 0.92;
  max-width: 520px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  position: relative;
  z-index: 1;
}

/* 场景条 - 占 1/3 高度 */
.scenarios-bar {
  flex: 1;
  min-height: 160px;
  background: white;
  border-radius: 20px;
  padding: 0;
  display: flex;
  align-items: stretch;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.scenario-tag {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px 24px;
  text-align: center;
  border-right: 1px solid #e2e8f0;
  transition: background 0.3s;
}

.scenario-tag:last-child {
  border-right: none;
}

.scenario-tag:hover {
  background: rgba(72, 187, 120, 0.05);
}

.scenario-tag .scenario-icon {
  font-size: 32px;
  flex-shrink: 0;
  color: #48bb78;
}

.scenario-tag .tag-title {
  font-weight: 600;
  color: #2d3748;
  font-size: 16px;
  line-height: 1.4;
}

.scenario-tag .tag-desc {
  color: #4a5568;
  font-size: 14px;
  line-height: 1.6;
}

/* 右侧列 */
.right-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  height: 100%;
}

/* 入口卡片 */
.entry-card {
  background: white;
  border-radius: 20px;
  padding: 0;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  transition: transform 0.3s, box-shadow 0.3s;
  height: 100%;
}

.entry-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 32px 28px 24px;
  text-align: center;
  border-bottom: 1px solid #f7fafc;
}

.entry-card .entry-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.entry-card h3 {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 8px 0;
}

.entry-card .entry-subtitle {
  font-size: 13px;
  color: #718096;
  margin: 0;
  line-height: 1.6;
}

.card-body {
  flex: 1;
  padding: 24px 28px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #4a5568;
  padding: 10px 0;
  border-bottom: 1px solid #f7fafc;
}

.feature-list li:last-child {
  border-bottom: none;
}

.check-icon {
  color: #48bb78;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
}

.card-footer {
  padding: 20px 28px 28px;
}

.action-button {
  width: 100%;
  padding: 14px 24px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.action-button.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-button.secondary {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35);
}



/* 头图卡片 */
.hero-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 48px 32px;
  text-align: center;
  color: white;
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.25);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  box-sizing: border-box;
}

.hero-card .hero-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 16px 0;
  letter-spacing: 1px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.hero-card .hero-subtitle {
  font-size: 14px;
  line-height: 1.8;
  margin: 0;
  opacity: 0.95;
  text-shadow: 0 1px 5px rgba(0, 0, 0, 0.3);
  max-width: 500px;
}




/* 系统简介 - 紧凑版 */
.intro-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.intro-section.compact {
  background: transparent;
  box-shadow: none;
  padding: 0;
  margin-bottom: 0;
}

.intro-section.compact .section-title {
  font-size: 28px;
  margin-bottom: 12px;
}

.intro-section.compact .intro-text {
  font-size: 14px;
  line-height: 1.8;
}

.intro-section.compact .intro-text.light {
  color: white;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
}

/* 适用场景 - 紧凑版 */
.scenarios-section.compact {
  background: white;
  padding: 14px 18px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.scenarios-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.scenario-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.scenario-dot {
  font-size: 20px;
  flex-shrink: 0;
}

.scenario-text {
  font-size: 13px;
  color: #2d3748;
  line-height: 1.5;
}

.scenario-text strong {
  font-weight: 600;
  color: #1a202c;
}

.scenario-divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.section-title {
  font-size: 20px;
  color: #303133;
  text-align: center;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.section-title.light {
  color: white;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
  margin: 0 0 16px 0;
}

.intro-text {
  font-size: 14px;
  color: #606266;
  text-align: center;
  line-height: 1.6;
  max-width: 900px;
  margin: 0 auto 20px;
}

/* 适用场景 */
.scenarios-section {
  background: rgba(255, 255, 255, 0.1);
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
}

.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.scenario-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 20px 16px;
  border-radius: 10px;
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.scenario-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.scenario-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.scenario-card h3 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.scenario-card p {
  font-size: 13px;
  color: #606266;
  margin: 0;
  line-height: 1.5;
}

/* 特性卡片 - 减小间距和高度 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: #f5f7fa;
  padding: 20px 16px;
  border-radius: 10px;
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.feature-card h3 {
  font-size: 16px;
  color: #303133;
  margin: 0 0 6px 0;
  font-weight: 600;
}

.feature-card p {
  font-size: 12px;
  color: #909399;
  margin: 0;
  line-height: 1.5;
}

/* 入口选择 - 紧凑版 */
.entry-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.entry-section.compact {
  background: transparent;
  box-shadow: none;
  padding: 0;
}



.entry-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.entry-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  border-top: 4px solid transparent;
  display: flex;
  flex-direction: column;
}

.entry-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.25);
}

.entry-card.customer {
  border-top-color: #67c23a;
}

.entry-card.admin {
  border-top-color: #409eff;
}

.entry-icon {
  font-size: 44px;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.entry-card h3 {
  font-size: 20px;
  color: #303133;
  margin: 0 0 6px 0;
  font-weight: 600;
  flex-shrink: 0;
}

.entry-card > p {
  font-size: 13px;
  color: #909399;
  margin: 0 0 14px 0;
  flex-shrink: 0;
}

.entry-features {
  list-style: none;
  padding: 0;
  margin: 0 0 16px 0;
  text-align: left;
  background: #f5f7fa;
  border-radius: 6px;
  padding: 14px;
  flex: 1;
  overflow-y: auto;
}

.entry-features li {
  font-size: 12px;
  color: #606266;
  padding: 4px 0;
  border-bottom: 1px solid #ebeef5;
  line-height: 1.4;
}

.entry-features li:last-child {
  border-bottom: none;
}

.entry-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 28px;
  font-size: 14px;
  border-radius: 24px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  flex-shrink: 0;
  font-weight: 600;
}

.entry-button:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

/* 响应式 */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .main-content {
    padding: 16px 20px 20px;
  }
}

@media (max-width: 768px) {
  .entry-cards {
    grid-template-columns: 1fr;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .logo h1 {
    font-size: 18px;
  }
  
  .main-content {
    padding: 12px 15px 15px;
  }
  
  .intro-section {
    padding: 18px;
  }
  
  .entry-section {
    padding: 18px;
  }
}
</style>
