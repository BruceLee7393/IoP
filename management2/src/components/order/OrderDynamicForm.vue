<template>
  <div class="order-dynamic-form">
    <el-form
      ref="formRef"
      :model="localFormData"
      :rules="rules"
      label-width="120px"
      @validate="handleValidate"
    >
      <!-- 订单基本信息表单 -->
      <template v-if="nodeType === 'order'">
        <el-form-item label="订单号" prop="order_number">
          <el-input 
            v-model="localFormData.order_number" 
            placeholder="请输入订单号"
            @input="handleFormChange"
          />
        </el-form-item>
        <el-form-item label="机型" prop="model">
          <el-input 
            v-model="localFormData.model" 
            placeholder="请输入机型"
            @input="handleFormChange"
          />
        </el-form-item>
        <el-form-item label="料号" prop="part_number">
          <el-input 
            v-model="localFormData.part_number" 
            placeholder="请输入料号"
            @input="handleFormChange"
          />
        </el-form-item>
        <el-form-item label="序列号范围" prop="serial_number_range">
          <el-input
            v-model="localFormData.serial_number_range"
            placeholder="请输入序列号范围，如：SNX1001-SNX1100 或 SNX1001~SNX1100"
            @input="handleSerialNumberRangeChange"
          />
          <template #append>
            <el-tooltip content="支持格式：起始-结束、起始--结束、起始~结束" placement="top">
              <el-icon><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
        </el-form-item>
        <el-form-item label="生产日期" prop="order_created_at">
          <el-date-picker
            v-model="localFormData.order_created_at"
            type="datetime"
            placeholder="请选择生产日期"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
            @change="handleFormChange"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="localFormData.remark"
            type="textarea"
            placeholder="请输入备注信息（可选）"
            :rows="3"
            maxlength="200"
            show-word-limit
            @input="handleFormChange"
          />
        </el-form-item>
      </template>

      <!-- 组件信息表单 -->
      <template v-else-if="nodeType === 'component'">
        <el-form-item label="组件名称" prop="component_name">
          <el-input 
            v-model="localFormData.component_name" 
            placeholder="请输入组件名称"
            @input="handleFormChange"
          />
        </el-form-item>
        <el-form-item label="组件料号" prop="component_part_number">
          <el-input 
            v-model="localFormData.component_part_number" 
            placeholder="请输入组件料号"
            @input="handleFormChange"
          />
        </el-form-item>
      </template>

      <!-- 子组件信息表单 -->
      <template v-else-if="nodeType === 'subComponent'">
        <el-form-item label="子组件名称" prop="sub_component_name">
          <el-input 
            v-model="localFormData.sub_component_name" 
            placeholder="请输入子组件名称"
            @input="handleFormChange"
          />
        </el-form-item>
        <el-form-item label="子组件料号" prop="sub_component_part_number">
          <el-input 
            v-model="localFormData.sub_component_part_number" 
            placeholder="请输入子组件料号"
            @input="handleFormChange"
          />
        </el-form-item>
        <el-form-item label="规格" prop="specification">
          <el-input 
            v-model="localFormData.specification" 
            placeholder="请输入规格（可选）"
            @input="handleFormChange"
          />
        </el-form-item>
      </template>

      <!-- 软件信息表单 -->
      <template v-else-if="nodeType === 'software'">
        <el-form-item label="软件名称" prop="software_name">
          <el-input 
            v-model="localFormData.software_name" 
            placeholder="请输入软件名称"
            @input="handleFormChange"
          />
        </el-form-item>
        <el-form-item label="软件版本" prop="software_version">
          <el-input 
            v-model="localFormData.software_version" 
            placeholder="请输入软件版本"
            @input="handleFormChange"
          />
        </el-form-item>
        <!-- <el-form-item label="附件" prop="attachment">
          <el-input 
            v-model="localFormData.attachment" 
            placeholder="请输入附件名称（可选）"
            @input="handleFormChange"
          />
        </el-form-item> -->
      </template>
    </el-form>

    <!-- 表单提示信息 -->
    <div v-if="nodeType === 'order'" class="form-tips">
      <el-alert
        title="提示"
        type="info"
        :closable="false"
        show-icon
      >
        <template #default>
          <p>请先完善订单基本信息，然后可以添加组件。</p>
          <p>组件 → 子组件 → 软件的层级结构将帮助您更好地管理订单内容。</p>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { Document, Cpu, Setting, Download, Plus, Delete, QuestionFilled } from '@element-plus/icons-vue'

const props = defineProps({
  nodeType: {
    type: String,
    required: true,
    validator: (value) => ['order', 'component', 'subComponent', 'software'].includes(value)
  },
  formData: {
    type: Object,
    required: true,
  },
  rules: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['form-change', 'form-validate'])

const formRef = ref(null)
const localFormData = ref({})

// 获取节点图标
const getNodeIcon = (nodeType) => {
  const iconMap = {
    order: Document,
    component: Cpu,
    subComponent: Setting,
    software: Download
  }
  return iconMap[nodeType] || Document
}

// 处理表单数据变化
const handleFormChange = () => {
  emit('form-change', { ...localFormData.value })
}

// 处理序列号范围变化
const handleSerialNumberRangeChange = () => {
  const range = localFormData.value.serial_number_range
  if (range) {
    // 支持多种分隔符：-、--、~
    let separator = null
    let parts = []

    if (range.includes('--')) {
      separator = '--'
      parts = range.split('--')
    } else if (range.includes('~')) {
      separator = '~'
      parts = range.split('~')
    } else if (range.includes('-')) {
      separator = '-'
      parts = range.split('-')
    }

    if (separator && parts.length >= 2) {
      const start = parts[0].trim()
      const end = parts[parts.length - 1].trim() // 取最后一部分作为结束
      localFormData.value.serial_number_start = start
      localFormData.value.serial_number_end = end
    }
  }
  handleFormChange()
}

// 处理表单验证
const handleValidate = (prop, valid, message) => {
  emit('form-validate', { prop, valid, message })
}

// 验证当前表单
const validateForm = async () => {
  if (!formRef.value) return false
  
  try {
    await formRef.value.validate()
    return true
  } catch {
    return false
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 监听表单数据变化
watch(() => props.formData, (newData) => {
  localFormData.value = { ...newData }

  // 如果是订单数据，合并序列号范围
  if (newData.serial_number_start && newData.serial_number_end) {
    localFormData.value.serial_number_range = `${newData.serial_number_start}-${newData.serial_number_end}`
  }
}, { immediate: true, deep: true })

// 暴露方法给父组件
defineExpose({
  validateForm,
  resetForm,
})
</script>

<style scoped>
.order-dynamic-form {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.form-tips {
  margin-top: 20px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

:deep(.el-input__wrapper) {
  border-radius: 6px;
}

:deep(.el-alert) {
  border-radius: 6px;
}

:deep(.el-alert__content) {
  line-height: 1.5;
}

:deep(.el-alert__content p) {
  margin: 4px 0;
}
</style>
