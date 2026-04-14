<template>
  <BaseDialog
    :model-value="modelValue"
    :title="`查看${entityName}详情`"
    width="800px"
    :show-confirm="false"
    cancel-text="关闭"
    @update:modelValue="emit('update:modelValue', $event)"
  >
    <slot name="view-content" :data="data">
      <div class="view-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item
            v-for="field in viewFields"
            :key="field.prop"
            :label="field.label"
            :span="field.type === 'textarea' ? 2 : 1"
          >
            <template v-if="field.type === 'textarea'">
              <div class="textarea-content">
                <el-input
                  :model-value="formatFieldValue(data, field)"
                  type="textarea"
                  :rows="field.rows || 8"
                  readonly
                  resize="none"
                />
              </div>
            </template>
            <template v-else>
              {{ formatFieldValue(data, field) }}
            </template>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </slot>
  </BaseDialog>
</template>

<script setup>
import BaseDialog from '@/components/base/BaseDialog.vue'

defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  entityName: {
    type: String,
    default: '记录',
  },
  viewFields: {
    type: Array,
    default: () => [],
  },
  data: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:modelValue'])

const formatFieldValue = (data, field) => {
  if (!data) return ''
  const value = data[field.prop]
  if (field.type === 'status') {
    return field.statusMap?.[value] || value
  }
  if (field.type === 'date') {
    return value ? new Date(value).toLocaleString() : ''
  }
  return value || ''
}
</script>

<style scoped>
.view-content {
  padding: 20px 0;
}

.textarea-content {
  width: 100%;
}

.textarea-content :deep(.el-textarea__inner) {
  background-color: #f5f7fa;
  border: 1px solid #dcdfe6;
  color: #606266;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.4;
  min-height: 200px;
}

.textarea-content :deep(.el-textarea) {
  width: 100%;
}
</style>
