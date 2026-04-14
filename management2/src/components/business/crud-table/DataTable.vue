<template>
  <BaseTable
    row-key="id"
    :data="data"
    :columns="columns"
    :loading="loading"
    :pagination="pagination"
    :actions="actions"
    :show-selection="showSelection"
    :show-index="showIndex"
    :show-expand="showExpand"
    @selection-change="emit('selection-change', $event)"
    @sort-change="emit('sort-change', $event)"
    @action="emit('action', $event)"
    @size-change="emit('size-change', $event)"
    @page-change="emit('page-change', $event)"
    @expand-change="(row, expanded) => emit('expand-change', row, expanded)"
  >
    <!-- 传递所有插槽 -->
    <template v-for="(_, name) in $slots" #[name]="slotData">
      <slot :name="name" v-bind="slotData" />
    </template>
  </BaseTable>
</template>

<script setup>
import BaseTable from '@/components/base/BaseTable.vue'

defineProps({
  data: {
    type: Array,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  pagination: {
    type: Object,
    default: () => ({}),
  },
  actions: {
    type: Array,
    default: () => [],
  },
  showSelection: {
    type: Boolean,
    default: true,
  },
  showIndex: {
    type: Boolean,
    default: true,
  },
  showExpand: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits([
  'selection-change',
  'sort-change',
  'action',
  'size-change',
  'page-change',
  'expand-change',
])
</script>
