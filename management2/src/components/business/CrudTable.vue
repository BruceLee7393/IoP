<template>
  <div class="crud-table">
    <!-- 查询表单 -->
    <BaseQueryForm
      v-if="showQueryForm"
      :query-params="queryParams"
      :fields="queryFields"
      :initial-query-params="initialQueryParams"
      :actions="queryActions"
      @search="handleSearch"
      @reset="handleReset"
      @action="handleQueryAction"
    />

    <!-- 表格卡片 -->
    <el-card class="table-card" shadow="never">
      <!-- 表格头部操作区 -->
      <ActionBar :title="title" :actions="headerActions" @action="handleHeaderAction">
        <template #title> </template>
      </ActionBar>

      <!-- 表格主体 -->
      <DataTable
        :data="tableData"
        :columns="tableColumns"
        :loading="loading"
        :pagination="paginationWithTotal"
        :actions="rowActions"
        :show-selection="showSelection"
        :show-index="showIndex"
        :show-expand="showExpand"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
        @action="handleRowAction"
        @size-change="handleSizeChange"
        @page-change="handlePageChange"
        @expand-change="handleExpandChange"
      >
        <!-- 传递所有插槽 -->
        <template v-for="(_, name) in $slots" #[name]="slotData">
          <slot :name="name" v-bind="slotData" />
        </template>
      </DataTable>
    </el-card>

    <!-- CRUD对话框 -->
    <CrudFormDialog
      v-if="formComponent"
      v-model="dialog.visible"
      :form-component="formComponent"
      :is-edit="dialog.isEdit"
      :initial-data="dialog.data"
      :form-props="formProps"
      @submit="submitForm"
      @submit-success="handleFormSuccess"
      @submitSuccess="handleFormSuccess"
    />

    <!-- 详情查看对话框 -->
    <component
      v-if="formComponent"
      :is="formComponent"
      v-model="viewDialog.visible"
      :is-view="true"
      :is-edit="false"
      :initial-data="viewDialog.data"
      v-bind="formProps"
    />
    <CrudViewDialog
      v-else
      v-model="viewDialog.visible"
      :entity-name="entityName"
      :view-fields="viewFields"
      :data="viewDialog.data"
    >
      <template #view-content="slotData">
        <slot name="view-content" v-bind="slotData" />
      </template>
    </CrudViewDialog>
  </div>
</template>

<script setup>
import { useCrudTable } from '@/composables/useCrudTable'
import BaseQueryForm from '@/components/base/BaseQueryForm.vue'
import ActionBar from './crud-table/ActionBar.vue'
import DataTable from './crud-table/DataTable.vue'
import CrudFormDialog from './crud-table/CrudFormDialog.vue'
import CrudViewDialog from './crud-table/CrudViewDialog.vue'

// Props定义
const props = defineProps({
  api: { type: Object, required: true },
  entityName: { type: String, default: '记录' },
  title: { type: String, default: '' },
  columns: { type: Array, required: true },
  queryFields: { type: Array, default: () => [] },
  viewFields: { type: Array, default: () => [] },
  formComponent: { type: [String, Object], default: null },
  formProps: { type: Object, default: () => ({}) },
  initialQueryParams: { type: Object, default: () => ({}) },
  showQueryForm: { type: Boolean, default: true },
  showSelection: { type: Boolean, default: true },
  showIndex: { type: Boolean, default: true },
  showExpand: { type: Boolean, default: false },
  customView: { type: Boolean, default: false },
  permissions: {
    type: Object,
    default: () => ({
      add: true,
      edit: true,
      delete: true,
      view: true,
      export: true,
    }),
  },
  headerActionConfig: { type: Object, default: () => ({}) },
  rowActionConfig: { type: Array, default: () => [] },
})

// Emits定义
const emit = defineEmits(['action', 'selection-change', 'expand-change', 'query-change'])

const {
  loading,
  tableData,
  queryParams,
  dialog,
  viewDialog,
  paginationWithTotal,
  tableColumns,
  headerActions,
  rowActions,
  queryActions,
  initialQueryParams,
  handleSearch,
  handleReset,
  handleQueryAction,
  handleHeaderAction,
  handleSelectionChange,
  handleSortChange,
  handleRowAction,
  handleSizeChange,
  handlePageChange,
  handleExpandChange,
  submitForm,
  handleFormSuccess,
  updateQueryParams,
} = useCrudTable(props, emit)

// 暴露方法给父组件
defineExpose({
  refresh: () => handleQueryAction({ event: 'refresh' }),
  updateQueryParams,
  handleSearch, // 暴露 handleSearch 方法
  handleReset, // 暴露 handleReset 方法
})
</script>

<style scoped>
.crud-table {
  width: 100%;
}
.table-card {
  margin-top: 16px;
}
</style>
