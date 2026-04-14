<template>
  <div class="role-management-container management-container">
    <CrudTable
      :api="api"
      entity-name="角色"
      :columns="tableColumns"
      :query-fields="queryFields"
      :form-component="RoleFormDialog"
      :initial-query-params="initialQueryParams"
      :permissions="permissions"
      :header-action-config="headerActionConfig"
      @action="handleCustomAction"
    >
      <template #cell-permissionConfig="{ row }">
        <el-button
          link
          type="success"
          class="permission-config-btn"
          @click="openPermissionDialog(row)"
        >
          配置权限
        </el-button>
      </template>

      <!-- 自定义状态列显示 -->
      <template #cell-status="{ row }">
        <el-switch
          v-model="row.status"
          :active-value="'active'"
          :inactive-value="'disabled'"
          inline-prompt
          active-text="启用"
          inactive-text="禁用"
          active-color="var(--el-color-success)"
          inactive-color="var(--el-color-danger)"
          :before-change="() => handleBeforeStatusChange(row)"
        />
      </template>
    </CrudTable>

    <RolePermissionDialog
      :visible="permissionDialogVisible"
      :role-info="selectedRole"
      @close="permissionDialogVisible = false"
      @success="handlePermissionSuccess"
    />
  </div>
</template>

<script setup>
import CrudTable from '@/components/business/CrudTable.vue'
import RoleFormDialog from '@/components/dialog/RoleFormDialog.vue'
import RolePermissionDialog from '@/components/dialog/RolePermissionDialog.vue'
import { useRoleManagement } from '@/composables/cfg/useRoleManagement'
import { useGlobalStore } from '@/stores/globalStore'

// 使用角色管理配置
const {
  crudTableRef,
  permissionDialogVisible,
  selectedRole,
  initialQueryParams,
  queryFields,
  tableColumns,
  permissions,
  headerActionConfig,
  api,
  handleCustomAction,
  handleBeforeStatusChange,
  openPermissionDialog,
  handlePermissionSuccess,
} = useRoleManagement()

// 成功后主动刷新角色下拉
const globalStore = useGlobalStore()
const onAfterSubmit = async () => {
  await globalStore.fetchRoleOptions(true)
}
</script>


