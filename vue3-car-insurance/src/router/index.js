import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // 首页 - 统一入口（无侧边栏）
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '智能业务决策平台' }
  },
  // ========== 智能服务入口 - 车险示例（无侧边栏） ==========
  {
    path: '/quote',
    name: 'Quote',
    component: () => import('../views/P01_Quote.vue'),
    meta: { title: '车险询价示例', subtitle: '演示 C 端用户实时决策场景' }
  },
  {
    path: '/quote/result',
    name: 'QuoteResult',
    component: () => import('../views/P02_Result.vue'),
    meta: { title: '智能决策结果', subtitle: '基于策略引擎的实时推荐' }
  },
  // ========== 策略中心入口（有侧边栏） ==========
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminHome.vue'),
    meta: { title: '策略中心' },
    redirect: '/admin/strategy/overview',
    children: [
      // 策略总览
      {
        path: 'strategy/overview',
        name: 'StrategyOverview',
        component: () => import('../views/strategy/StrategyOverview.vue'),
        meta: { title: '策略总览' }
      },
      // 策略工厂（新建/编辑策略）
      {
        path: 'strategy/create',
        name: 'StrategyCreate',
        component: () => import('../views/strategy/StrategyWizard.vue'),
        meta: { title: '策略工厂' }
      },
      {
        path: 'strategy/edit/:id',
        name: 'StrategyEdit',
        component: () => import('../views/strategy/StrategyWizard.vue'),
        meta: { title: '策略工厂' }
      },
      {
        path: 'strategy/detail/:id',
        name: 'StrategyDetail',
        component: () => import('../views/strategy/StrategyDetail.vue'),
        meta: { title: '策略详情' }
      },
      // 策略实验室（测试与历史）
      {
        path: 'strategy/history',
        name: 'StrategyHistory',
        component: () => import('../views/strategy/StrategyHistory.vue'),
        meta: { title: '策略实验室' }
      },
      {
        path: 'simulation-test',
        name: 'SimulationTest',
        component: () => import('../views/SimulationTest.vue'),
        meta: { title: '模拟测试' }
      },
      {
        path: 'ab-test',
        name: 'ABTest',
        component: () => import('../views/ABTest.vue'),
        meta: { title: 'A/B 测试' }
      },
      // 效果看板
      {
        path: 'effect-dashboard',
        name: 'EffectDashboard',
        component: () => import('../views/EffectDashboard.vue'),
        meta: { title: '效果看板' }
      },
      {
        path: 'publish',
        name: 'Publish',
        component: () => import('../views/Publish.vue'),
        meta: { title: '全量发布' }
      },
      // 业务分群与建模
      {
        path: 'business-unit',
        name: 'BusinessUnit',
        component: () => import('../views/BusinessUnit.vue'),
        meta: { title: '业务分群' }
      },
      {
        path: 'cost-simulation',
        name: 'CostSimulation',
        component: () => import('../views/CostSimulation.vue'),
        meta: { title: '成本建模' }
      },
      {
        path: 'revenue-simulation',
        name: 'RevenueSimulation',
        component: () => import('../views/RevenueSimulation.vue'),
        meta: { title: '收益预测' }
      },
      // 渠道管理（原保司配置）
      {
        path: 'insurer-priority',
        name: 'InsurerPriority',
        component: () => import('../views/InsurerPriority.vue'),
        meta: { title: '渠道管理' }
      },
      {
        path: 'insurer-intervention',
        name: 'InsurerIntervention',
        component: () => import('../views/InsurerIntervention.vue'),
        meta: { title: '动态调控' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from) => {
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 车险询价系统`
  }
  return true
})

export default router
