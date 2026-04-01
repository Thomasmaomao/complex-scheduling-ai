<template>
  <div class="strategy-layout">
    <!-- 顶部导航栏 -->
    <header class="layout-header">
      <div class="header-content">
        <div class="logo-area">
          <h1 class="logo-text">📊 策略配置中心</h1>
        </div>
        <div class="header-actions">
          <el-button text @click="handleBackToAdmin">
            <el-icon><ArrowLeft /></el-icon>
            返回管理首页
          </el-button>
          <el-divider direction="vertical" />
          <span class="user-info">{{ currentUser }}</span>
        </div>
      </div>
    </header>

    <div class="layout-body">
      <!-- 左侧边栏菜单 -->
      <aside class="sidebar">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          background-color="#ffffff"
          text-color="#606266"
          active-text-color="#667eea"
          router
        >
          <el-menu-item index="/admin/strategy/overview">
            <el-icon><Grid /></el-icon>
            <span>策略总览</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/strategy/create">
            <el-icon><Plus /></el-icon>
            <span>新建策略</span>
          </el-menu-item>

          <el-divider class="menu-divider" />

          <el-sub-menu index="history">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>历史记录</span>
            </template>
            <el-menu-item index="/admin/strategy/published">已发布策略</el-menu-item>
            <el-menu-item index="/admin/strategy/archived">已归档策略</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </aside>

      <!-- 主内容区域 -->
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Grid, Plus, Document } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const currentUser = '管理员'

const activeMenu = computed(() => {
  return route.path
})

const handleBackToAdmin = () => {
  router.push('/admin')
}
</script>

<style scoped>
.strategy-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

/* 顶部导航栏 */
.layout-header {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 24px;
}

.logo-area {
  display: flex;
  align-items: center;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  font-size: 13px;
  color: #606266;
}

/* 主体布局 */
.layout-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧边栏 */
.sidebar {
  width: 220px;
  background: white;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.sidebar-menu {
  border-right: none;
  padding: 16px 0;
}

.menu-divider {
  margin: 8px 16px;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
