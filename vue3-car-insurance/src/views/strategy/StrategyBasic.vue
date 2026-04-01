<template>
  <div class="strategy-basic">
    <div class="step-header">
      <h2>步骤 1/5：策略基本信息</h2>
      <p class="description">填写策略名称和生效机构</p>
    </div>

    <el-card class="form-card">
      <el-form 
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        label-position="top"
      >
        <el-form-item label="策略名称 *" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入策略名称，如：燃油车续保策略"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="策略描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入策略描述（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="生效机构 *" prop="institutions">
          <div class="institution-grid">
            <el-checkbox-group v-model="formData.institutions">
              <el-checkbox 
                v-for="inst in availableInstitutions" 
                :key="inst.code"
                :label="inst.code"
                border
              >
                {{ inst.name }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </el-form-item>

        <el-alert
          v-if="formData.institutions.length === 0"
          title="请至少选择一个生效机构"
          type="warning"
          :closable="false"
          show-icon
        />
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  strategyData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update', 'next'])

const formRef = ref(null)

// 可用机构列表
const availableInstitutions = [
  { code: 'shanghai', name: '上海' },
  { code: 'beijing', name: '北京' },
  { code: 'guangdong', name: '广东' },
  { code: 'zhejiang', name: '浙江' },
  { code: 'jiangsu', name: '江苏' },
  { code: 'sichuan', name: '四川' }
]

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  institutions: []
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入策略名称', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  institutions: [
    { required: true, message: '请至少选择一个生效机构', trigger: 'change' }
  ]
}

// 验证表单
const validateForm = async () => {
  try {
    await formRef.value?.validate()
    return true
  } catch (error) {
    return false
  }
}

// 监听数据变化
watch(() => formData, () => {
  const isValid = formData.name && formData.institutions.length > 0
  emit('update', {
    name: formData.name,
    description: formData.description,
    institutions: formData.institutions,
    isValid
  })
}, { deep: true })

// 加载已有数据（编辑模式）
onMounted(() => {
  if (props.strategyData?.id) {
    formData.name = props.strategyData.name || ''
    formData.description = props.strategyData.description || ''
    formData.institutions = props.strategyData.institutions || []
  }
})

// 暴露验证方法给父组件
defineExpose({
  validateForm
})
</script>

<style scoped>
.strategy-basic {
  padding: 24px;
}

.step-header {
  margin-bottom: 20px;
}

.step-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}

.description {
  font-size: 13px;
  color: #666;
  margin: 0;
}

.form-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.institution-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

:deep(.el-checkbox.is-bordered) {
  padding: 12px 16px;
  border-radius: 6px;
  border-color: #e4e7ed;
}

:deep(.el-checkbox.is-bordered.checked) {
  border-color: #667eea;
  background: #f5f7ff;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #667eea;
  border-color: #667eea;
}
</style>
