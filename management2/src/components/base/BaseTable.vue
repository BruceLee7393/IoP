<template>
  <div class="base-table">
    <!-- 表格主体 -->
    <el-table
      v-loading="loading"
      :data="data"
      :row-key="rowKey"
      stripe
      style="width: 100%"
      :border="border"
      :header-cell-style="headerCellStyle"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
      @expand-change="handleExpandChange"
    >
      <!-- 展开行 -->
      <el-table-column v-if="showExpand" type="expand" width="55" align="center">
        <template #default="{ row, $index }">
          <slot name="expand" :row="row" :index="$index" />
        </template>
      </el-table-column>
      <!-- 选择列 -->
      <el-table-column v-if="showSelection" type="selection" width="55" align="center" />
      <!-- 序号列 -->
      <el-table-column v-if="showIndex" type="index" label="序号" width="80" align="center" />
      <!-- 数据列 -->
      <el-table-column
        v-for="column in columns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
        :width="column.width"
        :min-width="column.minWidth"
        :sortable="column.sortable"
        :show-overflow-tooltip="column.showOverflowTooltip !== false"
        :align="column.align || 'left'"
        :fixed="column.fixed"
      >
        <template #default="{ row, column: tableColumn, $index }">
          <slot
            :name="`cell-${column.prop}`"
            :row="row"
            :column="tableColumn"
            :index="$index"
            :value="row[column.prop]"
          >
            <!-- 默认渲染逻辑 -->
            <template v-if="column.type === 'status'">
              <el-tag :type="getStatusType(row[column.prop])">
                {{ getStatusText(row[column.prop], column.statusMap) }}
              </el-tag>
            </template>
            <template v-else-if="column.type === 'date'">
              {{ formatDate(row[column.prop]) }}
            </template>
            <template v-else-if="column.formatter">
              {{ column.formatter(row, column, row[column.prop], $index) }}
            </template>
            <template v-else>
              {{ row[column.prop] }}
            </template>
          </slot>
        </template>
      </el-table-column>
      <!-- 操作列 -->
      <el-table-column
        v-if="actions && actions.length > 0"
        label="操作"
        :width="actionColumnWidth"
        :fixed="actionColumnFixed"
        align="center"
      >
        <template #default="{ row, $index }">
          <div class="table-actions">
            <template v-for="action in getVisibleActions(row)" :key="action.key">
              <el-button
                :type="getActionType(action, row)"
                :size="action.size || 'small'"
                :icon="action.icon"
                link
                :class="action.class || getActionClass(action)"
                :disabled="
                  typeof action.disabled === 'function' ? action.disabled(row) : action.disabled
                "
                @click="handleAction(action.event, row, $index)"
              >
                {{ getActionLabel(action, row) }}
              </el-button>
            </template>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页组件  -->
    <div v-if="showPagination && pagination" class="pagination-container">
      <el-pagination
        :current-page="pagination.page"
        :page-size="pagination.limit"
        :total="pagination.total"
        :page-sizes="pageSizes"
        :layout="paginationLayout"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>
  </div>
</template>
<script setup>
// Props 定义 (保持不变)
const props = defineProps({
  data: { type: Array, required: true },
  columns: { type: Array, required: true },
  actions: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  pagination: { type: Object, default: null },
  showSelection: { type: Boolean, default: true },
  showIndex: { type: Boolean, default: true },
  showExpand: { type: Boolean, default: false },
  showPagination: { type: Boolean, default: true },
  border: { type: Boolean, default: false },
  rowKey: { type: String, default: 'id' },
  headerCellStyle: {
    type: Object,
    default: () => ({ backgroundColor: '#f8f9fa', fontWeight: '600' }),
  },
  actionColumnWidth: { type: [String, Number], default: 180 },
  actionColumnFixed: { type: String, default: 'right' },
  pageSizes: { type: Array, default: () => [10, 20, 50, 100] },
  paginationLayout: { type: String, default: 'total, sizes, prev, pager, next, jumper' },
})
// Emits 定义
const emit = defineEmits([
  'selection-change',
  'sort-change',
  'action',
  'page-change',
  'size-change',
  'expand-change',
])
// 事件处理
const handleSelectionChange = (selection) => {
  emit('selection-change', selection)
}
const handleSortChange = (sortInfo) => {
  emit('sort-change', sortInfo)
}

const handleExpandChange = (row, expanded) => {
  emit('expand-change', row, expanded)
}
const handleAction = (event, row, index) => {
  emit('action', { event, row, index })
}
// 分页事件处理
const handlePageChange = (page) => {
  emit('page-change', page)
}
const handleSizeChange = (limit) => {
  emit('size-change', limit)
}
// 计算属性和工具函数 (保持不变)
const getVisibleActions = (row) =>
  props.actions.filter((action) => {
    // 支持 show 和 condition 两种条件判断方式
    if (action.show) return action.show(row)
    if (action.condition) return action.condition(row)
    return true
  })

// 获取动态标签
const getActionLabel = (action, row) => {
  if (typeof action.label === 'function') {
    return action.label(row)
  }
  if (action.render && typeof action.render === 'function') {
    const rendered = action.render(row)
    return rendered.label || action.label
  }
  return action.label
}

// 获取动态类型
const getActionType = (action, row) => {
  if (typeof action.type === 'function') {
    return action.type(row)
  }
  if (action.render && typeof action.render === 'function') {
    const rendered = action.render(row)
    return rendered.type || action.type || 'primary'
  }
  return action.type || 'primary'
}

const getStatusType = (status) =>
  ({
    true: 'success',
    false: 'danger',
    1: 'success',
    0: 'danger',
    enabled: 'success',
    disabled: 'danger',
    online: 'success',
    offline: 'danger',
  })[status] || 'info'

const getStatusText = (status, statusMap) =>
  (statusMap || {
    true: '启用',
    false: '禁用',
    1: '启用',
    0: '禁用',
    enabled: '启用',
    disabled: '禁用',
    online: '在线',
    offline: '离线',
  })[status] || status

const formatDate = (date) => (date ? new Date(date).toLocaleString() : '')

// 获取操作按钮的CSS类
const getActionClass = (action) => {
  const eventClassMap = {
    edit: 'btn-edit',
    delete: 'btn-delete',
    view: 'btn-view',
    download: 'btn-download',
    toggle: 'btn-toggle',
    create: 'btn-add',
    export: 'btn-export',
    upload: 'btn-upload',
    search: 'btn-search',
    reset: 'btn-reset',
  }
  return eventClassMap[action.event] || eventClassMap[action.key] || ''
}
</script>

<style scoped>
.base-table {
  width: 100%;
}
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding: 0 4px;
}
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}
:deep(.el-table__header-wrapper) {
  border-radius: 8px 8px 0 0;
}
:deep(.el-table__body-wrapper) {
  border-radius: 0 0 8px 8px;
}
/* 操作按钮容器 - 水平排列 */
.table-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  flex-wrap: nowrap;
}

/* 移除操作栏按钮的focus边框 */
.table-actions :deep(.el-button:focus) {
  outline: none !important;
  box-shadow: none !important;
}

.table-actions :deep(.el-button:focus-visible) {
  outline: none !important;
  box-shadow: none !important;
}

:deep(.el-tag) {
  border-radius: 4px;
  font-size: 12px;
}
</style>
