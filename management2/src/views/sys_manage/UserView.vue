<template>
  <div class="user-management-container management-container">
    <CrudTable
      ref="crudRef"
      :api="api"
      entity-name="用户"
      :columns="tableColumns"
      :query-fields="dynamicQueryFields"
      :form-component="UserFormDialog"
      :form-props="formProps"
      :initial-query-params="initialQueryParams"
      :permissions="permissions"
      :header-action-config="headerActionConfig"
      @action="handleCustomAction"
    >
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

      <template #cell-gender="{ row }">
        <span>{{ genderMap[row.gender] || '未知' }}</span>
      </template>

      <template #cell-role_name="{ row }">
        <el-tag v-if="getRoleName(row.role)" >{{ getRoleName(row.role) }}</el-tag>
        <span v-else class="text-muted">未分配</span>
      </template>


    </CrudTable>
  </div>
 </template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import CrudTable from '@/components/business/CrudTable.vue'
import UserFormDialog from '@/components/dialog/UserFormDialog.vue'
import { useGlobalStore } from '@/stores/globalStore'
// 【新增点2】从 composable 导入性别数据
import { useUserManagement, genderOptions, genderMap } from '@/composables/cfg/useUserManagement'

// 全局状态
const globalStore = useGlobalStore()
const { roleOptions } = storeToRefs(globalStore)

// 使用用户管理配置
const {
  initialQueryParams,
  dynamicQueryFields,
  tableColumns,
  permissions,
  headerActionConfig,
  api,
  initializeData,
  handleCustomAction,
  handleBeforeStatusChange,
} = useUserManagement()

// 表单组件属性
const formProps = computed(() => ({
  roleOptions: Array.isArray(roleOptions.value) ? roleOptions.value : [],
  // 将性别选项传递给表单弹窗
  genderOptions: genderOptions,
}))

// 初始化数据
onMounted(async () => {
  await initializeData()
  // 监听全局实体变更事件：角色变化后刷新角色选项和表格
  if (typeof window !== 'undefined') {
    window.addEventListener('entity-changed', async (e) => {
      const name = e?.detail?.entityName?.toLowerCase?.() || ''
      if (name.includes('角色') || name.includes('role')) {
        await globalStore.fetchRoleOptions(true)
        // 刷新当前表格数据
        crudRef?.value?.refresh?.()
      }
    })
  }
})

// 获取角色名称
const getRoleName = (roleData) => {
  // 如果roleData是对象，直接从对象中获取名称
  if (roleData && typeof roleData === 'object') {
    return roleData.role_name || roleData.name || roleData.label || ''
  }

  

  return ''
}



// 生命周期
onMounted(() => {
  globalStore.fetchRoleOptions()
})
const crudRef = ref(null)
</script>

<style scoped>
.user-management-container {
  padding: 20px;
}

.text-muted {
  color: #909399;
}
</style>