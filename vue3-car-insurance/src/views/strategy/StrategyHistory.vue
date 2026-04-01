<template>
  <div class="strategy-history">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>策略历史记录</h1>
      <el-input
        v-model="keyword"
        placeholder="搜索策略名称或版本"
        style="width: 300px"
        clearable
        @input="filterHistory"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>
    
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="策略">
          <el-select 
            v-model="filters.strategy_id" 
            placeholder="全部策略" 
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="strategy in strategies"
              :key="strategy.id"
              :label="strategy.name"
              :value="strategy.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select 
            v-model="filters.operation_type" 
            placeholder="全部类型" 
            clearable
            style="width: 150px"
          >
            <el-option label="创建" value="create" />
            <el-option label="编辑" value="edit" />
            <el-option label="发布" value="publish" />
            <el-option label="回滚" value="rollback" />
            <el-option label="禁用" value="disable" />
            <el-option label="启用" value="enable" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadHistory">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 历史记录列表 -->
    <el-card class="history-card">
      <el-timeline>
        <el-timeline-item
          v-for="record in historyList"
          :key="record.id"
          :timestamp="formatDate(record.created_at)"
          placement="top"
          :type="getOperationType(record.operation_type)"
        >
          <el-card shadow="hover">
            <div class="history-item">
              <div class="history-header">
                <h4>{{ record.strategy_name }}</h4>
                <el-tag :type="getOperationTagType(record.operation_type)">
                  {{ getOperationLabel(record.operation_type) }}
                </el-tag>
              </div>
              
              <div class="history-content">
                <p><strong>版本号:</strong> v{{ record.version_number }}</p>
                <p><strong>操作人:</strong> {{ record.created_by || '系统' }}</p>
                <p><strong>变更摘要:</strong> {{ record.change_summary || '-' }}</p>
              </div>
              
              <div class="history-actions">
                <el-button 
                  size="small" 
                  @click="viewVersion(record.id)"
                >
                  查看详情
                </el-button>
                <el-button 
                  v-if="record.operation_type !== 'rollback'"
                  size="small" 
                  type="warning"
                  @click="rollbackToVersion(record.id)"
                >
                  回滚到此版本
                </el-button>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      
      <!-- 空状态 -->
      <el-empty v-if="historyList.length === 0" description="暂无历史记录" />
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        layout="total, prev, pager, next"
        @current-change="loadHistory"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
    
    <!-- 版本详情对话框 -->
    <el-dialog
      v-model="versionDialogVisible"
      title="版本详情"
      width="800px"
    >
      <div v-if="currentVersion" class="version-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="策略名称">
            {{ currentVersion.strategy_name }}
          </el-descriptions-item>
          <el-descriptions-item label="版本号">
            v{{ currentVersion.version_number }}
          </el-descriptions-item>
          <el-descriptions-item label="操作人">
            {{ currentVersion.created_by || '系统' }}
          </el-descriptions-item>
          <el-descriptions-item label="操作时间">
            {{ formatDate(currentVersion.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="操作类型">
            <el-tag :type="getOperationTagType(currentVersion.operation_type)">
              {{ getOperationLabel(currentVersion.operation_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="变更摘要">
            {{ currentVersion.change_summary || '-' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin-top: 20px;">策略快照</h4>
        <pre class="snapshot-json">{{ JSON.stringify(currentVersion.snapshot_data, null, 2) }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getStrategyHistory, getVersionDetail, rollbackStrategy } from '../../api/strategy'

// 搜索
const keyword = ref('')

// 筛选条件
const filters = reactive({
  strategy_id: '',
  operation_type: '',
  date_range: []
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 数据
const strategies = ref([])
const historyList = ref([])
const versionDialogVisible = ref(false)
const currentVersion = ref(null)

// 加载历史记录
const loadHistory = async () => {
  try {
    const params = {
      ...filters,
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    const response = await getStrategyHistory(params)
    historyList.value = response.data.history || []
    pagination.total = response.data.total || 0
    
    // 加载策略列表用于筛选
    strategies.value = response.data.strategies || []
  } catch (error) {
    ElMessage.error('加载历史记录失败：' + error.message)
  }
}

// 筛选历史记录
const filterHistory = () => {
  pagination.page = 1
  loadHistory()
}

// 查看详情
const viewVersion = async (versionId) => {
  try {
    const response = await getVersionDetail(versionId)
    currentVersion.value = response.data
    versionDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载版本详情失败：' + error.message)
  }
}

// 回滚到指定版本
const rollbackToVersion = async (versionId) => {
  try {
    await ElMessageBox.confirm(
      '确定要回滚到此版本吗？此操作不可逆。',
      '确认回滚',
      { type: 'warning' }
    )
    
    await rollbackStrategy(versionId)
    ElMessage.success('回滚成功')
    loadHistory()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('回滚失败：' + error.message)
    }
  }
}

// 格式化日期
const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

// 获取操作类型标签
const getOperationLabel = (type) => {
  const labels = {
    create: '创建',
    edit: '编辑',
    publish: '发布',
    rollback: '回滚',
    disable: '禁用',
    enable: '启用'
  }
  return labels[type] || type
}

const getOperationTagType = (type) => {
  const types = {
    create: 'success',
    edit: '',
    publish: 'primary',
    rollback: 'warning',
    disable: 'danger',
    enable: 'success'
  }
  return types[type] || ''
}

const getOperationType = (type) => {
  const types = {
    create: 'success',
    edit: '',
    publish: 'primary',
    rollback: 'warning',
    disable: 'danger',
    enable: 'success'
  }
  return types[type] || ''
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.strategy-history {
  padding: 20px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .filter-card {
    margin-bottom: 20px;
  }
  
  .history-card {
    .el-timeline {
      padding: 20px 0;
    }
    
    .history-item {
      .history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        
        h4 {
          margin: 0;
          font-size: 16px;
          color: #303133;
        }
      }
      
      .history-content {
        p {
          margin: 8px 0;
          font-size: 14px;
          color: #606266;
        }
      }
      
      .history-actions {
        margin-top: 15px;
        display: flex;
        gap: 10px;
      }
    }
    
    .el-pagination {
      display: flex;
    }
  }
  
  .version-detail {
    .snapshot-json {
      max-height: 400px;
      overflow-y: auto;
      background: #f5f7fa;
      padding: 15px;
      border-radius: 4px;
      font-family: 'Courier New', monospace;
      font-size: 12px;
    }
  }
}
</style>
