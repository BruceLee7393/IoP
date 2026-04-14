<template>
  <!-- 动态组件渲染 -->
  <component
    v-if="formComponent"
    :is="formComponent"
    :model-value="modelValue"
    :is-edit="isEdit"
    :initial-data="initialData"
    v-bind="formProps"
    @update:modelValue="emit('update:modelValue', $event)"
    @submit="emit('submit', $event)"
    @submit-success="emit('submit-success', $event)"
    @submitSuccess="emit('submit-success', $event)"
  />

  <!-- 通用表单Dialog -->
  <BaseFormDialog
    v-else
    :model-value="modelValue"
    :title="title || (isEdit ? '编辑' : '新增')"
    :form-data="formData"
    :rules="rules"
    :loading="loading"
    v-bind="dialogProps"
    @update:modelValue="emit('update:modelValue', $event)"
    @confirm="handleSubmit"
    @cancel="handleCancel"
    @closed="handleClosed"
  >
    <!-- 动态表单字段渲染 -->
    <template v-for="field in fields" :key="field.prop">
      <el-form-item :label="field.label" :prop="field.prop" :required="field.required">
        <!-- 根据字段类型渲染不同组件 -->
        <component
          :is="getFieldComponent(field.type)"
          v-model="formData[field.prop]"
          v-bind="field.props"
        />
      </el-form-item>
    </template>

    <!-- 插槽支持自定义字段 -->
    <slot :form-data="formData" :is-edit="isEdit" :loading="loading" />
  </BaseFormDialog>
</template>

<script setup>
import { ref } from 'vue'
import BaseFormDialog from '@/components/base/BaseFormDialog.vue'

defineProps({
  formComponent: {
    type: [String, Object],
    required: true,
  },
  modelValue: {
    type: Boolean,
    default: false,
  },
  isEdit: {
    type: Boolean,
    default: false,
  },
  initialData: {
    type: Object,
    default: () => ({}),
  },
  formProps: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:modelValue', 'submit', 'submit-success'])

// 添加缺失的方法和状态
const formData = ref({})
const loading = ref(false)

const handleSubmit = () => {
  emit('submit', formData.value)
}

const handleCancel = () => {
  emit('update:modelValue', false)
}

const handleClosed = () => {
  formData.value = {}
}

const getFieldComponent = (type) => {
  const componentMap = {
    input: 'el-input',
    select: 'el-select',
    date: 'el-date-picker',
    datetime: 'el-date-picker',
    textarea: 'el-input',
    number: 'el-input-number',
  }
  return componentMap[type] || 'el-input'
}
</script>
