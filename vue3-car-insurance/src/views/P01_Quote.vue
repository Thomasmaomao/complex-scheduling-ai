<template>
  <div class="quote-page">
    <!-- 顶部标题 -->
    <header class="page-header">
      <div class="header-content">
        <button class="back-home" @click="goHome">
          <span>←</span> 返回首页
        </button>
        <div class="page-title">
          <h1>🚗 车险询价示例</h1>
          <p class="page-subtitle">演示 C 端用户实时决策场景 — 平台能力可应用于金融科技 | SaaS 服务 | 保险科技</p>
        </div>
      </div>
    </header>

    <!-- 表单内容 -->
    <main class="form-container">
      <el-form
        ref="quoteFormRef"
        :model="quoteForm"
        :rules="formRules"
        label-width="120px"
        class="quote-form"
      >
        <!-- 车辆信息 -->
        <section class="form-section">
          <h2 class="section-title">车辆信息</h2>
          <div class="form-grid">
            <el-form-item label="车牌号码" prop="licensePlate">
              <el-input v-model="quoteForm.licensePlate" placeholder="例：沪 A·88888" clearable />
            </el-form-item>
            <el-form-item label="车架号" prop="vin">
              <el-input v-model="quoteForm.vin" placeholder="请输入 17 位车架号" maxlength="17" clearable />
            </el-form-item>
            <el-form-item label="注册日期" prop="registrationDate">
              <el-date-picker v-model="quoteForm.registrationDate" type="date" placeholder="年/月/日" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="能源类型" prop="fuelType">
              <el-select v-model="quoteForm.fuelType" placeholder="燃油车" style="width: 100%">
                <el-option label="燃油车" value="gasoline" />
                <el-option label="纯电动" value="electric" />
                <el-option label="混合动力" value="hybrid" />
              </el-select>
            </el-form-item>
            <el-form-item label="新车购置价" prop="vehicleValue">
              <el-input-number v-model="quoteForm.vehicleValue" :min="0" :precision="0" :step="1000" controls-position="right" placeholder="请输入购置价（元）" style="width: 100%" />
            </el-form-item>
            <el-form-item label="承保区域" prop="region">
              <el-select v-model="quoteForm.region" placeholder="上海市" style="width: 100%">
                <el-option label="上海市" value="shanghai" />
              </el-select>
            </el-form-item>
          </div>
        </section>

        <!-- 车主信息 -->
        <section class="form-section owner-section">
          <h2 class="section-title">车主信息</h2>
          <div class="form-grid">
            <el-form-item label="真实姓名" prop="ownerName">
              <el-input v-model="quoteForm.ownerName" placeholder="请输入姓名" clearable />
            </el-form-item>
            <el-form-item label="身份证号" prop="idCard">
              <el-input v-model="quoteForm.idCard" placeholder="请输入 18 位身份证号" maxlength="18" clearable />
            </el-form-item>
          </div>
          <p class="age-tip-full">系统自动识别：{{ calculatedAge || '--' }}岁</p>
        </section>

        <!-- 险种选择 -->
        <section class="form-section insurance-section">
          <h2 class="section-title">险种选择</h2>
          <div class="insurance-list">
            <!-- 交强险 -->
            <div class="insurance-item compulsory">
              <div class="insurance-left">
                <span class="insurance-icon">🛡️</span>
                <div class="insurance-info">
                  <span class="insurance-name">交强险</span>
                  <span class="insurance-tag">国家强制</span>
                </div>
              </div>
              <el-checkbox v-model="checkedTypes.compulsory" />
            </div>

            <!-- 第三者责任险 -->
            <div class="insurance-item">
              <div class="insurance-left">
                <span class="insurance-icon">🚗</span>
                <div class="insurance-info">
                  <span class="insurance-name">第三者责任险</span>
                </div>
              </div>
              <div class="insurance-right">
                <el-select v-model="thirdPartyLimit" size="small" placeholder="300 万" class="coverage-select">
                  <el-option label="100 万" :value="1000000" />
                  <el-option label="200 万" :value="2000000" />
                  <el-option label="300 万" :value="3000000" />
                  <el-option label="500 万" :value="5000000" />
                </el-select>
                <el-checkbox v-model="checkedTypes.third_party" />
              </div>
            </div>

            <!-- 车辆损失险 -->
            <div class="insurance-item">
              <div class="insurance-left">
                <span class="insurance-icon">🚙</span>
                <span class="insurance-name">车辆损失险</span>
              </div>
              <div class="insurance-right">
                <span class="coverage-display">保额：¥{{ vehicleValueDisplay }}万</span>
                <el-checkbox v-model="checkedTypes.vehicle_damage" />
              </div>
            </div>

            <!-- 司机责任险 -->
            <div class="insurance-item">
              <div class="insurance-left">
                <span class="insurance-icon">👨‍💼</span>
                <span class="insurance-name">司机责任险</span>
              </div>
              <div class="insurance-right">
                <span class="coverage-display">保额：{{ driverCoverageDisplay }}</span>
                <el-select v-model="driverCoverage" size="small" class="coverage-select">
                  <el-option label="1 万" :value="10000" />
                  <el-option label="2 万" :value="20000" />
                  <el-option label="5 万" :value="50000" />
                  <el-option label="10 万" :value="100000" />
                </el-select>
                <el-checkbox v-model="checkedTypes.driver" />
              </div>
            </div>

            <!-- 乘客责任险 -->
            <div class="insurance-item">
              <div class="insurance-left">
                <span class="insurance-icon">👨‍👩‍👧‍👦</span>
                <span class="insurance-name">乘客责任险</span>
              </div>
              <div class="insurance-right">
                <span class="coverage-display">保额：{{ passengerCoverageDisplay }}/座</span>
                <el-select v-model="passengerCoverage" size="small" class="coverage-select">
                  <el-option label="1 万" :value="10000" />
                  <el-option label="2 万" :value="20000" />
                  <el-option label="5 万" :value="50000" />
                  <el-option label="10 万" :value="100000" />
                </el-select>
                <el-checkbox v-model="checkedTypes.passenger" />
              </div>
            </div>


          </div>
        </section>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <el-button type="primary" size="large" :loading="isSubmitting" @click="handleSubmit" class="submit-button">
            获取报价
            <el-icon><ArrowRight /></el-icon>
          </el-button>
          <p class="security-notice">
            <el-icon><Lock /></el-icon>
            您的隐私信息将受到金融级安全保护
          </p>
        </div>
      </el-form>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { calculateQuote } from '../api/quote'
import { ArrowRight, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const quoteFormRef = ref(null)
const isSubmitting = ref(false)
const thirdPartyLimit = ref(3000000)
const driverCoverage = ref(50000)
const passengerCoverage = ref(50000)

const checkedTypes = reactive({
  compulsory: true,
  third_party: true,
  vehicle_damage: false,
  driver: false,
  passenger: false
})

const quoteForm = reactive({
  licensePlate: '',
  vin: '',
  registrationDate: '',
  fuelType: 'gasoline',
  vehicleValue: null,
  region: 'shanghai',
  ownerName: '',
  idCard: '',
  insuranceTypes: ['compulsory', 'third_party']
})

const vehicleValueDisplay = computed(() => {
  return quoteForm.vehicleValue ? (quoteForm.vehicleValue / 10000).toFixed(0) : ''
})

const driverCoverageDisplay = computed(() => {
  return driverCoverage.value >= 10000 ? (driverCoverage.value / 10000).toFixed(0) + '万' : ''
})

const passengerCoverageDisplay = computed(() => {
  return passengerCoverage.value >= 10000 ? (passengerCoverage.value / 10000).toFixed(0) + '万' : ''
})

watch(checkedTypes, (newVal) => {
  quoteForm.insuranceTypes = Object.keys(newVal).filter(key => newVal[key])
}, { deep: true })

const calculatedAge = computed(() => {
  if (!quoteForm.idCard || quoteForm.idCard.length !== 18) return ''
  const birthYear = parseInt(quoteForm.idCard.substring(6, 10))
  return new Date().getFullYear() - birthYear
})

const formRules = {
  licensePlate: [{ required: true, message: '请输入车牌号', trigger: 'blur' }],
  vin: [
    { required: true, message: '请输入车架号', trigger: 'blur' },
    { pattern: /^[A-HJ-NPR-Z0-9]{17}$/, message: '车架号必须为 17 位', trigger: 'blur' }
  ],
  registrationDate: [{ required: true, message: '请选择初登日期', trigger: 'change' }],
  fuelType: [{ required: true, message: '请选择燃料类型', trigger: 'change' }],
  vehicleValue: [
    { required: true, message: '请输入新车购置价', trigger: 'blur' },
    { type: 'number', min: 0, message: '购置价必须大于 0', trigger: 'blur' }
  ],
  region: [{ required: true, message: '请选择地区', trigger: 'change' }],
  ownerName: [{ required: true, message: '请输入车主姓名', trigger: 'blur' }],
  idCard: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/, message: '身份证号格式不正确', trigger: 'blur' }
  ]
}

const goHome = () => router.push('/')

const handleSubmit = async () => {
  if (!quoteFormRef.value) return
  await quoteFormRef.value.validate(async (valid) => {
    if (valid) {
      isSubmitting.value = true
      try {
        const apiData = {
          license_plate: quoteForm.licensePlate,
          vin: quoteForm.vin,
          registration_date: quoteForm.registrationDate,
          fuel_type: quoteForm.fuelType,
          vehicle_value: quoteForm.vehicleValue ? quoteForm.vehicleValue : null,
          region: quoteForm.region,
          owner_name: quoteForm.ownerName,
          id_card: quoteForm.idCard,
          insurance_types: quoteForm.insuranceTypes,
        }
        console.log('提交询价数据:', apiData)
        const result = await calculateQuote(apiData)
        console.log('报价结果:', result)
        if (result && result.quotes) {
          sessionStorage.setItem('quoteResult', JSON.stringify(result))
          router.push('/quote/result')
          ElMessage.success('获取报价成功')
        } else {
          ElMessage.error('报价结果格式错误')
        }
      } catch (error) {
        console.error('询价错误:', error)
        ElMessage.error('获取报价失败：' + (error.message || '请稍后重试'))
      } finally {
        isSubmitting.value = false
      }
    } else {
      ElMessage.warning('请填写完整的表单信息')
    }
  })
}
</script>

<style scoped>
.quote-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.page-header {
  background: white;
  padding: 10px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
  position: relative;
}

.back-home {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: none;
  color: #606266;
  cursor: pointer;
  font-size: 13px;
  padding: 4px 8px;
}

.page-title h1 {
  font-size: 18px;
  color: #1a73e8;
  margin: 0;
  font-weight: 600;
}

.page-subtitle {
  font-size: 11px;
  color: #1a73e8;
  margin: 2px 0 0 0;
}

.form-container {
  flex: 1;
  max-width: 800px;
  margin: 0 auto;
  padding: 12px 16px 16px;
  width: 100%;
}

.form-section {
  background: white;
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.section-title {
  font-size: 14px;
  color: #303133;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.owner-section {
  background: #fafbfc;
  padding: 14px 16px;
}

.age-tip-full {
  margin: 8px 0 0 120px;
  font-size: 12px;
  color: #1a73e8;
}

.insurance-right {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
}

.coverage-display {
  font-size: 12px;
  color: #909399;
  margin-right: 8px;
  white-space: nowrap;
}

.insurance-section {
  padding: 14px 16px;
}

.insurance-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.insurance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.insurance-item:last-child {
  border-bottom: none;
}

.insurance-item.compulsory {
  background: #f0f7ff;
  padding: 10px 12px;
  border-radius: 8px;
  border-bottom: none;
}

.insurance-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.insurance-icon {
  font-size: 18px;
}

.insurance-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.insurance-name {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.insurance-tag {
  font-size: 10px;
  color: #52c41a;
  background: #f6ffed;
  padding: 1px 4px;
  border-radius: 4px;
  border: 1px solid #b7eb8f;
}

.coverage-select {
  width: 85px;
}

.form-actions {
  text-align: center;
  padding: 14px 0 8px;
}

.submit-button {
  width: 100%;
  height: 42px;
  font-size: 15px;
  font-weight: 600;
  background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.security-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 11px;
  color: #909399;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .back-home {
    position: static;
    transform: none;
    margin-bottom: 8px;
  }
}
</style>
