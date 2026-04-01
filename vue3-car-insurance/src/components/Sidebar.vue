<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="logo-wrapper">
        <div class="logo-icon">🚗</div>
        <div class="logo-text">
          <h2>车险询价系统</h2>
          <p>策略配置大脑</p>
        </div>
      </div>
    </div>
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="isCollapse"
      background-color="#1a1f2e"
      text-color="#a0aec0"
      active-text-color="#ffffff"
      :unique-opened="true"
    >
      <!-- 策略配置中心 -->
      <el-sub-menu index="1">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>策略配置中心</span>
        </template>
        <el-menu-item index="1-1" @click="navigateTo('/admin/strategy/business-unit')">业务单元划分</el-menu-item>
        <el-menu-item index="1-2" @click="navigateTo('/admin/strategy/cost-simulation')">成本模拟</el-menu-item>
        <el-menu-item index="1-3" @click="navigateTo('/admin/strategy/revenue-simulation')">收益模拟</el-menu-item>
      </el-sub-menu>

      <!-- 策略测试中心 -->
      <el-sub-menu index="2">
        <template #title>
          <el-icon><Document /></el-icon>
          <span>策略测试中心</span>
        </template>
        <el-menu-item index="2-1" @click="navigateTo('/admin/strategy/simulation-test')">模拟测试</el-menu-item>
        <el-menu-item index="2-2" @click="navigateTo('/admin/strategy/ab-test')">A/B 测试</el-menu-item>
      </el-sub-menu>

      <!-- 发布与效果分析中心 -->
      <el-sub-menu index="3">
        <template #title>
          <el-icon><DataAnalysis /></el-icon>
          <span>发布与效果分析</span>
        </template>
        <el-menu-item index="3-1" @click="navigateTo('/admin/strategy/effect-dashboard')">效果看板</el-menu-item>
        <el-menu-item index="3-2" @click="navigateTo('/admin/strategy/publish')">全量发布</el-menu-item>
      </el-sub-menu>

      <!-- 保司配置中心 -->
      <el-sub-menu index="4">
        <template #title>
          <el-icon><OfficeBuilding /></el-icon>
          <span>保司配置中心</span>
        </template>
        <el-menu-item index="4-1" @click="navigateTo('/admin/insurer/priority')">保司优先级配置</el-menu-item>
        <el-menu-item index="4-2" @click="navigateTo('/admin/insurer/monitoring')">保司动态监控</el-menu-item>
      </el-sub-menu>

      <!-- 客户询价（独立菜单） -->
      <el-menu-item index="5" @click="navigateTo('/quote')">
        <el-icon><ShoppingCart /></el-icon>
        <span>客户询价</span>
      </el-menu-item>
    </el-menu>
    <div class="sidebar-footer">
      <el-menu-item @click="navigateTo('/')">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回首页</span>
      </el-menu-item>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Setting,
  Document,
  DataAnalysis,
  OfficeBuilding,
  ShoppingCart,
  ArrowLeft
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const isCollapse = ref(false)

const activeMenu = computed(() => {
  return route.path
})

const navigateTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: 100vh;
  background: linear-gradient(180deg, #1a1f2e 0%, #162032 100%);
  position: fixed;
  left: 0;
  top: 0;
  overflow-y: auto;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.logo-text h2 {
  color: #ffffff;
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.5px;
}

.logo-text p {
  color: #718096;
  font-size: 11px;
  margin: 2px 0 0 0;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background: transparent;
  padding: 12px 0;
}

:deep(.el-menu) {
  border-right: none;
  background: transparent;
}

:deep(.el-sub-menu__title) {
  color: #a0aec0;
  font-size: 13px;
  font-weight: 500;
  padding-left: 24px !important;
  transition: all 0.2s ease;
}

:deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.08) !important;
  color: #ffffff;
}

:deep(.el-menu-item) {
  color: #a0aec0;
  font-size: 13px;
  padding-left: 48px !important;
  transition: all 0.2s ease;
}

:deep(.el-menu-item:hover) {
  background-color: rgba(64, 158, 255, 0.15) !important;
  color: #ffffff;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(64, 158, 255, 0.2) 0%, transparent 100%) !important;
  color: #ffffff !important;
  border-left: 3px solid #409EFF;
  padding-left: 45px !important;
}

:deep(.el-icon) {
  font-size: 18px;
  margin-right: 8px;
}

.sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px 0;
  background: rgba(0, 0, 0, 0.2);
}

:deep(.sidebar-footer .el-menu-item) {
  color: #718096;
  font-size: 13px;
  padding-left: 24px !important;
}

:deep(.sidebar-footer .el-menu-item:hover) {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.05) !important;
}
</style>
