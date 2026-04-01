<template>
  <div class="common-layout">
    <el-container>
      <!-- 左侧边栏 -->
      <el-aside width="240px" class="sidebar-aside">
        <div class="logo-container">
          <span class="logo-text">策略中心</span>
          <span class="logo-subtitle">车险策略示例</span>
        </div>
        <el-menu
          default-active="/admin/strategy/overview"
          :default-openeds="['1', '2', '3', '4']"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          :router="false"
        >
          <el-sub-menu index="1">
            <template #title>
              <el-icon><setting /></el-icon>
              <span>🏭 策略工厂</span>
            </template>
            <el-menu-item index="1-1" @click="navigateTo('/admin/strategy/overview')">策略总览</el-menu-item>
            <el-menu-item index="1-2" @click="navigateTo('/admin/strategy/create')">新建策略</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="2">
            <template #title>
              <el-icon><document /></el-icon>
              <span>🧪 策略实验室</span>
            </template>
            <el-menu-item index="2-1" @click="navigateTo('/admin/simulation-test')">模拟测试</el-menu-item>
            <el-menu-item index="2-2" @click="navigateTo('/admin/ab-test')">A/B 测试</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="3">
            <template #title>
              <el-icon><data-analysis /></el-icon>
              <span>📈 效果看板</span>
            </template>
            <el-menu-item index="3-1" @click="navigateTo('/admin/publish')">全量发布</el-menu-item>
            <el-menu-item index="3-2" @click="navigateTo('/admin/effect-dashboard')">效果看板</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="4">
            <template #title>
              <el-icon><office-building /></el-icon>
              <span>⚙️ 渠道管理</span>
            </template>
            <el-menu-item index="4-1" @click="navigateTo('/admin/insurer-priority')">渠道管理</el-menu-item>
            <el-menu-item index="4-2" @click="navigateTo('/admin/insurer-intervention')">动态调控</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="5" @click="navigateTo('/')">
            <el-icon><arrow-left /></el-icon>
            <span>返回首页</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <el-main class="main-content">
          <router-view :key="$route.fullPath" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import {
  Setting,
  Document,
  DataAnalysis,
  OfficeBuilding,
  ArrowLeft
} from '@element-plus/icons-vue'

const router = useRouter()

const navigateTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.common-layout {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.sidebar-aside {
  background-color: #304156;
  overflow-x: hidden;
}

.logo-container {
  height: 70px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4b;
  border-bottom: 1px solid #3d4a5c;
  padding: 10px 0;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
}

.logo-subtitle {
  color: #9ca3af;
  font-size: 12px;
  margin-top: 4px;
}

.el-menu-vertical {
  border-right: none;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
