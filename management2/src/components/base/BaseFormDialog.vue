<template>
  <BaseDialog
    :model-value="modelValue"
    :title="title"
    :width="width"
    :loading="loading"
    :show-cancel="showCancel"
    :show-confirm="showConfirm"
    :confirm-text="confirmText"
    :cancel-text="cancelText"
    @update:modelValue="emit('update:modelValue', $event)"
    @confirm="handleConfirm"
    @cancel="handleCancel"
    @closed="handleClosed"
  >
    <BaseForm
      ref="formRef"
      :model="formData"
      :rules="rules"
      :label-width="labelWidth"
      :label-position="labelPosition"
      :inline="false"
      @submit="handleSubmit"
    >
      <slot :form-data="formData" :loading="loading" />
    </BaseForm>
  </BaseDialog>
</template>

<script setup>
import { ref } from 'vue'
import BaseDialog from './BaseDialog.vue'
import BaseForm from './BaseForm.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '表单',
  },
  width: {
    type: String,
    default: '600px',
  },
  formData: {
    type: Object,
    required: true,
  },
  rules: {
    type: Object,
    default: () => ({}),
  },
  loading: {
    type: Boolean,
    default: false,
  },
  labelWidth: {
    type: String,
    default: '100px',
  },
  labelPosition: {
    type: String,
    default: 'right',
  },
  showCancel: {
    type: Boolean,
    default: true,
  },
  showConfirm: {
    type: Boolean,
    default: true,
  },
  confirmText: {
    type: String,
    default: '确定',
  },
  cancelText: {
    type: String,
    default: '取消',
  },
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel', 'closed', 'submit'])

const formRef = ref(null)

const handleConfirm = async () => {
  try {
    await formRef.value?.validate()
    emit('confirm', props.formData)
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const handleCancel = () => {
  emit('cancel')
}

const handleClosed = () => {
  formRef.value?.resetFields()
  emit('closed')
}

const handleSubmit = (formData) => {
  emit('submit', formData)
}

// 暴露表单方法
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  clearValidate: () => formRef.value?.clearValidate(),
})
</script>
