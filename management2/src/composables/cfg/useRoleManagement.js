// src/composables/cfg/useRoleManagement.js
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import * as roleApi from '@/api/role'

/**
 * 角色管理业务逻辑
 */
export function useRoleManagement() {
  const crudTableRef = ref(null)
  const permissionDialogVisible = ref(false)
  const selectedRole = ref({})

  // 初始查询参数（使用驼峰命名）
  const initialQueryParams = {
    roleCode: '',
    roleName: '',
    status: undefined,
  }

  // 查询字段配置（使用驼峰命名）
  const queryFields = [
    {
      prop: 'roleCode',
      label: '角色编码',
      type: 'input',
      placeholder: '请输入角色编码',
      span: 6,
    },
    {
      prop: 'roleName',
      label: '角色名称',
      type: 'input',
      placeholder: '请输入角色名称',
      span: 6,
    },
    {
      prop: 'status',
      label: '状态',
      type: 'select',
      options: [
        { label: '启用', value: 'active' },
        { label: '禁用', value: 'disabled' },
      ],
      span: 4,
    },
  ]

  // 表格列配置
  const tableColumns = [
    {
      prop: 'role_code',
      label: '角色编码',
      minWidth: 120,
      // align: 'center',
      sortable: true,
    },
    {
      prop: 'role_name',
      label: '角色名称',
      // align: 'center',
      minWidth: 120,
      sortable: true,
    },

    {
      prop: 'status',
      label: '状态',
      width: 100,
      align: 'center',
      type: 'status',
      statusMap: {
        active: '启用',
        disabled: '禁用',
      },
    },
    {
      prop: 'description',
      label: '描述',
      minWidth: 150,
      sortable: false,
      align: 'left',
      showOverflowTooltip: true,
    },
    { prop: 'created_at', label: '创建时间', minWidth: 160 ,
      formatter: (row) => formatDateTime(row.created_at),
    },

    {
      prop: 'permissionConfig',
      label: '权限配置',
      width: 130,
      sortable: false,
      align: 'left',
      type: 'permissionConfig',
    },
  ]

  // 权限配置
  const permissions = computed(() => ({
    add: true,
    edit: true,
    delete: true,
    view: false,
    export: true,
  }))
  const rowActionConfig = [
    { key: 'edit', label: '修改', type: 'primary', event: 'edit', size: 'small' },
    { key: 'delete', label: '删除', type: 'danger', event: 'delete', size: 'small' },
  ]

  const formatDateTime = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // 自定义头部按钮样式
  const headerActionConfig = {
    batchDelete: { type: 'danger', icon: 'Delete' },
    export: { type: 'success', icon: 'Download' },
  }

  // 状态变更前确认
  const handleBeforeStatusChange = async (role) => {
    const newStatus = role.status === 'active' ? 'disabled' : 'active' // 计算新状态
    const newStatusText = newStatus === 'active' ? '启用' : '禁用'
    try {
      await ElMessageBox.confirm(
        `确定要"${newStatusText}"角色 [${role.role_name}] 吗？`,
        '状态变更确认',
        { type: 'warning' },
      )
      await roleApi.updateRole(role.id, { status: newStatus }) // 传递新状态
      ElMessage.success(`角色 [${role.role_name}] 已成功${newStatusText}`)
      return true
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error(`操作失败: ${error?.msg || '未知错误'}`)
      }
      return false
    }
  }

  // 打开权限配置弹窗
  const openPermissionDialog = (row) => {
    selectedRole.value = { ...row }
    permissionDialogVisible.value = true
  }

  // 权限配置成功处理
  const handlePermissionSuccess = () => {
    // 权限配置更新后，可以触发相关数据刷新
    // 这里可以根据需要添加额外的逻辑
    // console.log('权限更新成功')

    // 发送权限变更事件，触发全局权限数据刷新
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('entity-changed', {
        detail: { entityName: '权限', action: 'update' }
      }))
    }
  }

  // API配置 - 参照用户管理的实现
  const api = {
    // 获取列表
    async getList(params) {
      try {

        const response = await roleApi.getRoleList(params)

        // apiUtils.js已经返回标准格式{records, total}，直接返回
        return response
      } catch (error) {
        console.error('获取角色列表失败:', error)
        ElMessage.error('获取角色列表失败')
        throw error
      }
    },

    // 创建角色
    async create(data) {
      try {
        const result = await roleApi.createRole(data)
        return result
      } catch (error) {
        console.error('创建角色失败:', error)
        throw error
      }
    },

    // 更新角色
    async update(id, data) {
      try {
        const result = await roleApi.updateRole(id, data)
        return result
      } catch (error) {
        console.error('更新角色失败:', error)
        throw error
      }
    },

    // 删除角色
    async delete(id) {
      try {
        await roleApi.deleteRole(id)
        return true
      } catch (error) {
        console.error('删除角色失败:', error)
        // 检查是否是后端返回的成功消息被当作错误处理
        if (
          error.message &&
          (error.message.includes('删除成功') ||
            error.message.includes('角色删除成功') ||
            error.message === 'success')
        ) {
          return true
        }
        throw error // 重新抛出真正的错误，让useCrud处理
      }
    },

    // 批量删除
    async batchDelete(ids) {
      try {
        await roleApi.batchDeleteRole(ids)
        // 移除重复的消息提示，由useCrud统一处理
        return true
      } catch (error) {
        console.error('批量删除失败:', error)
        throw error // 重新抛出错误，让useCrud处理
      }
    },

    // 导出
    async export(params) {
      try {

        // 调用后端导出API
        await roleApi.exportRoles(params)
        ElMessage.success('导出请求已发送，文件将自动下载')
        return true
      } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败')
        return false
      }
    },
  }

  // 自定义操作处理
  const handleCustomAction = ({ type, action, data }) => {
    switch (action) {
      default:
        return Promise.resolve(false)
    }
  }

  return {
    // 响应式数据
    crudTableRef,
    permissionDialogVisible,
    selectedRole,


    // 配置
    initialQueryParams,
    queryFields,
    tableColumns,
    permissions,
    rowActionConfig,
    headerActionConfig,

    // API
    api,

    // 方法
    handleCustomAction,
    handleBeforeStatusChange,
    openPermissionDialog,
    handlePermissionSuccess,
  }
}
