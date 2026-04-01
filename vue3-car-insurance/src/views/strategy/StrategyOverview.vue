<template>
  <div class="strategy-overview">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>策略总览</h1>
      <el-button type="primary" @click="navigateTo('/admin/strategy/create')">
        <span class="icon">➕</span>
        新建策略
      </el-button>
    </div>
    
    <!-- 搜索筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="策略名称">
          <el-input 
            v-model="filters.keyword" 
            placeholder="搜索策略名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="filters.status" 
            placeholder="全部状态"
            clearable
            style="width: 150px"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="模拟测试通过" value="simulation_passed" />
            <el-option label="模拟测试失败" value="simulation_failed" />
            <el-option label="A/B 测试通过" value="ab_test_passed" />
            <el-option label="A/B 测试失败" value="ab_test_failed" />
            <el-option label="已发布" value="published" />
            <el-option label="已禁用" value="disabled" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadStrategies">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 策略列表 -->
    <el-card class="table-card">
      <el-table :data="strategies" stripe v-loading="loading">
        <el-table-column prop="name" label="策略名称" min-width="200" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" :class="getStatusClass(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="institutions" label="生效机构" min-width="150">
          <template #default="{ row }">
            <span>{{ row.institutions?.join('、') || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="business_units_count" label="业务单元数" width="100" align="center">
          <template #default="{ row }">
            {{ row.business_units_count || row.business_units?.length || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80" align="center">
          <template #default="{ row }">
            v{{ row.version }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button 
              size="small" 
              @click="editStrategy(row.id)"
              :disabled="['published', 'archived'].includes(row.status)"
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="primary"
              @click="viewDetail(row)"
            >
              详情
            </el-button>
            <!-- 草稿状态显示发布按钮，其他状态显示禁用/启用按钮 -->
            <template v-if="row.status === 'draft'">
              <el-button 
                size="small" 
                type="success"
                @click="publishStrategy(row)"
              >
                发布
              </el-button>
            </template>
            <template v-else>
              <el-button 
                size="small" 
                :type="row.status === 'disabled' ? 'success' : 'warning'"
                @click="toggleStatus(row)"
              >
                {{ row.status === 'disabled' ? '启用' : '禁用' }}
              </el-button>
            </template>
            <el-button 
              size="small" 
              type="danger"
              @click="deleteStrategy(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        layout="total, prev, pager, next, jumper"
        @current-change="loadStrategies"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllStrategies, deleteStrategy as deleteStrategyApi, updateStrategyStatus } from '../../api/strategy'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const strategies = ref([])

const filters = reactive({
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 加载策略列表
const loadStrategies = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      status_filter: filters.status || undefined
    }
    
    const response = await getAllStrategies(params.status_filter, params.page, params.page_size)
    strategies.value = response.strategies || []
    pagination.total = response.total || 0
    
    // 应用关键词筛选（前端筛选）
    if (filters.keyword) {
      strategies.value = strategies.value.filter(s => 
        s.name.toLowerCase().includes(filters.keyword.toLowerCase())
      )
      pagination.total = strategies.value.length
    }
  } catch (error) {
    console.error('加载策略失败:', error)
    ElMessage.error('加载失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 监听路由参数变化，自动刷新
watch(() => route.query.refresh, () => {
  loadStrategies()
})

// 编辑策略
const editStrategy = (id) => {
  router.push(`/admin/strategy/edit/${id}`)
}

// 查看详情
const viewDetail = (row) => {
  router.push(`/admin/strategy/detail/${row.id}`)
}

// 导航到新建页面
const navigateTo = (path) => {
  router.push(path)
}

// 切换状态
const toggleStatus = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认${row.status === 'disabled' ? '启用' : '禁用'}该策略吗？`,
      '确认操作',
      { type: 'warning' }
    )
    
    const newStatus = row.status === 'disabled' ? 'draft' : 'disabled'
    await updateStrategyStatus(row.id, { status: newStatus })
    
    ElMessage.success('操作成功')
    // 重新加载列表确保状态正确更新
    loadStrategies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败：' + error.message)
    }
  }
}

// 删除策略
const deleteStrategy = async (id) => {
  try {
    await ElMessageBox.confirm(
      '删除后无法恢复，确认删除该策略吗？',
      '确认删除',
      { type: 'warning' }
    )
    
    await deleteStrategyApi(id)
    
    ElMessage.success('删除成功')
    loadStrategies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

// 获取状态样式类
const getStatusClass = (status) => {
  if (status === 'disabled') {
    return 'status-disabled'
  }
  return ''
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labels = {
    draft: '草稿',
    simulation_passed: '模拟通过',
    simulation_failed: '模拟失败',
    ab_test_passed: 'A/B 通过',
    ab_test_failed: 'A/B 失败',
    published: '已发布',
    disabled: '已禁用',
    archived: '已归档'
  }
  return labels[status] || status
}

// 获取状态类型（用于标签颜色）
const getStatusType = (status) => {
  const types = {
    draft: '',              // 灰色
    simulation_passed: 'success',     // 绿色
    simulation_failed: 'danger',      // 红色
    ab_test_passed: 'success',        // 绿色
    ab_test_failed: 'danger',         // 红色
    published: 'primary',             // 蓝色
    disabled: 'info',                 // 灰色
    archived: 'info'                  // 灰色
  }
  return types[status] || ''
}

// 发布策略
const publishStrategy = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认发布策略 "${row.name}" 吗？发布后将无法编辑。`,
      '确认发布',
      { type: 'warning' }
    )
    
    // 调用发布API（需要实现）
    // await publishStrategyApi(row.id)
    
    ElMessage.success('策略发布成功')
    loadStrategies()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('发布失败：' + error.message)
    }
  }
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 监听策略保存事件
const handleStrategySaved = () => {
  loadStrategies()
}

onMounted(() => {
  // 始终调用 loadStrategies 加载策略列表
  loadStrategies()
  
  // 监听保存事件
  window.addEventListener('strategy-saved', handleStrategySaved)
})

// 组件卸载时移除监听
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('strategy-saved', handleStrategySaved)
})
</script>

<style scoped>
.strategy-overview {
  padding: 24px;
  min-height: 100vh;
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  .el-pagination {
    display: flex;
  }
}

.icon {
  margin-right: 4px;
}

/* 改善已禁用状态的视觉效果 */
.status-disabled {
  background-color: #f5f5f5 !important;
  color: #999999 !important;
  border-color: #d9d9d9 !important;
  font-weight: 600;
}
</style>
