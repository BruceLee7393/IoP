<template>
  <div class="table-header">
    <div class="table-title">
      <slot name="title">
        <h3>{{ title }}</h3>
      </slot>
    </div>
    <div class="table-actions">
      <BaseActionButtons :actions="actions" @action="handleAction" />
    </div>
  </div>
</template>

<script setup>
import BaseActionButtons from '@/components/base/BaseActionButtons.vue'

defineProps({
  title: {
    type: String,
    default: '',
  },
  actions: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['action'])

const handleAction = (action) => {
  emit('action', action)
}
</script>

<style scoped>
.table-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 16px;
  gap: 20px;
}

.table-title h3 {
  margin: 0;
  color: #303133;
  font-weight: 600;
}

@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>
