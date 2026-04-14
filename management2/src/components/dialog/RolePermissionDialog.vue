<!-- src/components/dialog/RolePermissionDialog.vue -->
<template>
  <BaseDialog
    :model-value="visible"
    :title="`配置权限 - ${roleInfo.role_name || ''}`"
    width="600px"
    @cancel="handleClose"
    @confirm="handleConfirm"
    :loading="loading"
  >
    <div class="permission-config">
      <div class="permission-header">
        <span class="label">权限列表：</span>
        <div class="batch-actions">
          <el-button
            size="small"
            type="primary"
            plain
            @click="selectAll"
            :disabled="loading"
          >
            全选
          </el-button>
          <el-button
            size="small"
            @click="clearAll"
            :disabled="loading"
          >
            清空
          </el-button>
        </div>
      </div>

      <div class="permission-list" v-loading="permissionLoading">
        <el-tree
          ref="permissionTreeRef"
          :data="permissionTreeData"
          :props="treeProps"
          show-checkbox
          node-key="id"
          :default-checked-keys="selectedPermissions"
          :check-strictly="false"
          @check="handleTreeCheck"
          class="permission-tree"
        >
          <template #default="{ data }">
            <div class="tree-node">
              <el-icon v-if="data.icon" class="node-icon">
                <component :is="data.icon" />
              </el-icon>
              <span class="node-label">{{ data.name }}</span>
              <span v-if="data.code" class="node-code">({{ data.code }})</span>
            </div>
          </template>
        </el-tree>
      </div>

      <div class="permission-summary">
        已选择 <strong>{{ selectedPermissions.length }}</strong> 项权限，
        共 <strong>{{ allPermissions.length }}</strong> 项权限
      </div>
    </div>
  </BaseDialog>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import BaseDialog from '@/components/base/BaseDialog.vue'
import { getAllPermissions, getRolePermissions, addRolePermissions, removeRolePermissions } from '@/api/permission'
import { buildPermissionTree, extractPermissionIds, setTreeCheckedState } from '@/utils/permissionGrouper'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  roleInfo: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['close', 'success'])

const loading = ref(false)
const permissionLoading = ref(false)
const allPermissions = ref([])
const selectedPermissions = ref([])
const originalPermissions = ref([]) // 原始权限，用于对比变化
const permissionTreeRef = ref(null)
const permissionTreeData = ref([])

// 树组件配置
const treeProps = {
  children: 'children',
  label: 'name',
}



// 获取所有权限列表
const fetchAllPermissions = async () => {
  try {
    permissionLoading.value = true
    const response = await getAllPermissions()
    console.log('所有权限API响应:', response)

    // 处理不同的响应格式
    let permissions = []
    if (Array.isArray(response)) {
      permissions = response
    } else if (response && response.code === 0 && Array.isArray(response.data)) {
      permissions = response.data
    } else if (response && Array.isArray(response.data)) {
      permissions = response.data
    }

    allPermissions.value = permissions
    // 构建权限树（权限配置弹窗：包含模块节点）
    permissionTreeData.value = buildPermissionTree(permissions, {
      includeModuleNodes: true,
      onlyUserPermissions: false
    })
  } catch (error) {
    console.error('获取权限列表失败:', error)
    ElMessage.error('获取权限列表失败')
  } finally {
    permissionLoading.value = false
  }
}

// 获取角色当前权限
const fetchRolePermissions = async (roleId) => {
  if (!roleId) return

  try {
    permissionLoading.value = true
    const response = await getRolePermissions(roleId)
    console.log('角色权限API响应:', response)

    // 处理不同的响应格式
    let rolePermissions = []
    if (Array.isArray(response)) {
      rolePermissions = response
    } else if (response && response.code === 0 && Array.isArray(response.data)) {
      rolePermissions = response.data
    } else if (response && Array.isArray(response.data)) {
      rolePermissions = response.data
    }

    selectedPermissions.value = rolePermissions.map(p => p.id)
    originalPermissions.value = [...selectedPermissions.value]

    // 设置树的选中状态
    if (permissionTreeRef.value && permissionTreeData.value.length > 0) {
      const checkedNodeIds = setTreeCheckedState(permissionTreeData.value, selectedPermissions.value)
      permissionTreeRef.value.setCheckedKeys(checkedNodeIds)
    }
  } catch (error) {
    console.error('获取角色权限失败:', error)
    ElMessage.error('获取角色权限失败')
  } finally {
    permissionLoading.value = false
  }
}

// 处理树节点选择
const handleTreeCheck = (data, { checkedKeys, halfCheckedKeys }) => {
  // 收集所有选中的权限ID（包括半选状态的父节点）
  const allCheckedIds = []

  const collectPermissionIds = (nodes, checkedKeys) => {
    nodes.forEach(node => {
      if (node.permissionId && checkedKeys.includes(node.id)) {
        allCheckedIds.push(node.permissionId)
      }
      if (node.children) {
        collectPermissionIds(node.children, checkedKeys)
      }
    })
  }

  collectPermissionIds(permissionTreeData.value, checkedKeys)
  selectedPermissions.value = allCheckedIds
}

// 全选
const selectAll = () => {
  if (permissionTreeRef.value) {
    const allPermissionIds = extractPermissionIds(permissionTreeData.value)
    const allNodeIds = setTreeCheckedState(permissionTreeData.value, allPermissionIds)
    permissionTreeRef.value.setCheckedKeys(allNodeIds)
    selectedPermissions.value = allPermissionIds
  }
}

// 清空
const clearAll = () => {
  if (permissionTreeRef.value) {
    permissionTreeRef.value.setCheckedKeys([])
    selectedPermissions.value = []
  }
}

// 计算需要添加和删除的权限
const getPermissionChanges = () => {
  const current = new Set(selectedPermissions.value)
  const original = new Set(originalPermissions.value)

  const toAdd = selectedPermissions.value.filter(id => !original.has(id))
  const toRemove = originalPermissions.value.filter(id => !current.has(id))

  return { toAdd, toRemove }
}

// 确认配置
const handleConfirm = async () => {
  if (!props.roleInfo.id) return

  const { toAdd, toRemove } = getPermissionChanges()

  // 如果没有变化，直接关闭
  if (toAdd.length === 0 && toRemove.length === 0) {
    ElMessage.info('权限配置未发生变化')
    handleClose()
    return
  }

  try {
    loading.value = true

    // 批量删除权限
    if (toRemove.length > 0) {
      await removeRolePermissions(props.roleInfo.id, toRemove)
    }

    // 批量添加权限
    if (toAdd.length > 0) {
      await addRolePermissions(props.roleInfo.id, toAdd)
    }

    ElMessage.success('权限配置更新成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('更新权限配置失败:', error)
    ElMessage.error('更新权限配置失败')
  } finally {
    loading.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  emit('close')
}

// 重置状态
const resetState = () => {
  selectedPermissions.value = []
  originalPermissions.value = []
  allPermissions.value = []
}

// 监听对话框显示状态
watch(
  () => props.visible,
  async (newVisible) => {
    if (newVisible) {
      resetState()
      await fetchAllPermissions()
      if (props.roleInfo.id) {
        // 等待权限树构建完成后再获取角色权限
        await nextTick()
        await fetchRolePermissions(props.roleInfo.id)
      }
    }
  }
)


</script>

<style scoped>
.permission-config {
  max-height: 500px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.permission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.permission-header .label {
  font-weight: 500;
  color: #303133;
}

.batch-actions {
  display: flex;
  gap: 8px;
}

.permission-list {
  flex: 1;
  overflow-y: auto;
  max-height: 350px;
  padding: 8px 0;
}

.permission-item {
  margin-bottom: 12px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.permission-item:hover {
  background-color: #f5f7fa;
}

.permission-name {
  font-weight: 500;
  color: #303133;
  margin-right: 8px;
}

.permission-code {
  color: #909399;
  font-size: 12px;
}

.permission-summary {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  text-align: center;
  color: #606266;
  font-size: 14px;
}

.permission-summary strong {
  color: #409eff;
}

.permission-tree {
  width: 100%;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding: 4px 0;
}

.node-icon {
  font-size: 16px;
  color: #606266;
}

.node-label {
  font-weight: 500;
  color: #303133;
}

.node-code {
  color: #909399;
  font-size: 12px;
  font-weight: normal;
}

:deep(.el-tree-node__content) {
  height: auto;
  padding: 4px 0;
}

:deep(.el-tree-node__label) {
  flex: 1;
}

:deep(.el-tree-node) {
  margin-bottom: 2px;
}

:deep(.el-tree-node:focus > .el-tree-node__content) {
  background-color: #f5f7fa;
}

:deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}
</style>
