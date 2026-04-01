<template>
  <div class="welcome-page">
    <div class="welcome-section">
      <h2>欢迎使用平台管理系统</h2>
      <p>请选择左侧菜单进行操作</p>
      
      <div class="module-grid">
        <div class="module-card">
          <div class="module-icon">📋</div>
          <h3>策略配置中心</h3>
          <p>配置业务单元、成本模拟、收益分析</p>
        </div>
        <div class="module-card">
          <div class="module-icon">🧪</div>
          <h3>策略测试中心</h3>
          <p>模拟测试、A/B 测试验证策略效果</p>
        </div>
        <div class="module-card">
          <div class="module-icon">📊</div>
          <h3>发布与效果分析</h3>
          <p>策略发布、效果监控、数据分析</p>
        </div>
        <div class="module-card">
          <div class="module-icon">🏢</div>
          <h3>保司配置中心</h3>
          <p>保司优先级配置、动态监控</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 平台管理欢迎页面
</script>

<style scoped>
.welcome-page {
  padding: 40px;
}

.welcome-section {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.welcome-section h2 {
  font-size: 28px;
  color: #303133;
  margin: 0 0 10px 0;
}

.welcome-section > p {
  font-size: 15px;
  color: #909399;
  margin: 0 0 40px 0;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.module-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.module-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.module-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.module-card h3 {
  font-size: 18px;
  color: #303133;
  margin: 0 0 10px 0;
}

.module-card p {
  font-size: 13px;
  color: #909399;
  margin: 0;
  line-height: 1.6;
}

@media (max-width: 1200px) {
  .module-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
