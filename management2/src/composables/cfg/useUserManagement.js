// src/composables/cfg/useUserManagement.js
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as userApi from '@/api/user'
import { useGlobalStore } from '@/stores/globalStore'


export const genderMap = {
  man: '男',
  woman: '女',
  others: '其他',
  none: '不愿透露',
}

export const genderOptions = [
  { value: 'man', label: '男' },
  { value: 'woman', label: '女' },
  { value: 'others', label: '其他' },
  { value: 'none', label: '不愿透露性别' },
]

/**
 * 用户管理 UI 配置和 API 调用
 */
export function useUserManagement() {

  const dateShortcuts = [
    {
      text: '今天',
      value: () => {
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        const end = new Date(today)
        end.setHours(23, 59, 59, 999)
        return [today, end]
      },
    },
    {
      text: '昨天',
      value: () => {
        const start = new Date()
        start.setTime(start.getTime() - 3600 * 1000 * 24)
        start.setHours(0, 0, 0, 0)
        const end = new Date(start)
        end.setHours(23, 59, 59, 999)
        return [start, end]
      },
    },
    {
      text: '最近一周',
      value: () => {
        const end = new Date()
        const start = new Date()
        start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
        return [start, end]
      },
    },
    {
      text: '最近一个月',
      value: () => {
        const end = new Date()
        const start = new Date()
        start.setMonth(start.getMonth() - 1)
        return [start, end]
      },
    },
    {
      text: '最近三个月',
      value: () => {
        const end = new Date()
        const start = new Date()
        start.setMonth(start.getMonth() - 3)
        return [start, end]
      },
    },
  ]

  const crudTableRef = ref(null)
  const globalStore = useGlobalStore()
  // 角色选项直接引用全局store，保持实时更新
  const roleOptions = computed(() => Array.isArray(globalStore.roleOptions) ? globalStore.roleOptions : [])

  //  修改初始查询参数，使用单个范围字段
  const initialQueryParams = {
    account: '',
    fullName: '',
    role: '',
    contactInfo: '',
    address: '',
    status: '',
    gender: '',
    created_at_range: null, // 使用 created_at_range 代替 start 和 end
  }

  // 【关键修改3】: 修改查询字段配置，合并为单个日期范围选择器
  const queryFields = [
    {
      prop: 'account',
      label: '账号',
      type: 'input',
      placeholder: '请输入账号',
      span: 4,
    },
    {
      prop: 'fullName',
      label: '用户姓名',
      type: 'input',
      placeholder: '请输入用户姓名',
      span: 4,
    },
    {
      prop: 'gender',
      label: '性别',
      type: 'select',
      placeholder: '请选择性别',
      options: genderOptions,
      span: 4,
    },
    {
      prop: 'role',
      label: '角色',
      type: 'select',
      placeholder: '请选择角色',
      options: [], // 由外部传入
      clearable: true,
      filterable: true,
      span: 4,
    },

    {
      prop: 'contactInfo',
      label: '联系方式',
      type: 'input',
      placeholder: '请输入联系方式',
      span: 4,
    },
    {
      prop: 'address',
      label: '地址',
      type: 'input',
      placeholder: '请输入地址',
      span: 4,
    },
    {
      prop: 'created_at_range',
      label: '创建时间',
      type: 'datetimerange',
      span: 8,
      startPlaceholder: '开始日期',
      endPlaceholder: '结束日期',
      shortcuts: dateShortcuts,
    },
    {
      prop: 'status',
      label: '状态',
      type: 'select',
      placeholder: '请选择状态',
      options: [
        { label: '启用', value: 'active' },
        { label: '禁用', value: 'disabled' },
      ],
      span: 4,
    },
  ]

  // 表格列配置 - 纯展示配置
  const tableColumns = [
    {
      prop: 'account',
      label: '账号',
      minWidth: 120,
      sortable: 'custom',
    },
    {
      prop: 'full_name',
      label: '用户姓名',
      minWidth: 120,
      sortable: 'custom',
    },
    {
      prop: 'gender',
      label: '性别',
      minWidth: 120,
      sortable: false,
      slot: 'gender', // 指定使用名为 gender 的插槽
    },
    {
      prop: 'role_name',
      label: '角色',
      minWidth: 150,
      sortable: 'custom',
    },

    {
      prop: 'contact_info',
      label: '联系方式',
      minWidth: 120,
      sortable: 'custom',
    },
    {
      prop: 'address',
      label: '地址',
      minWidth: 150,
      sortable: 'false',
      showOverflowTooltip: true,
    },
    {
      prop: 'created_at',
      label: '创建时间',
      minWidth: 180,
      align: 'center',
      sortable: 'custom',
      type: 'datetime',
      formatter: (row) => formatDateTime(row.created_at),
    },
    {
      prop: 'status',
      label: '状态',
      width: 120,
      align: 'center',
      sortable: 'custom',
      type: 'status',
      statusMap: {
        active: '启用',
        disabled: '禁用',
      },
    },
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
  // 权限配置
  const permissions = computed(() => ({
    add: true,
    edit: true,
    delete: true,
    batchDelete: true, // 启用批量删除
    view: false, // 禁用详情查看
    export: true, // 启用导出功能
  }))

  // 头部操作配置
  const headerActionConfig = {
    showAdd: true,
    showExport: true, // 启用导出功能
    showBatchDelete: true, // 启用批量删除
    customActions: [],
  }

  // 行操作配置
  const rowActionConfig = [
    {
      key: 'edit',
      label: '编辑',
      type: 'primary',
      event: 'edit',
      size: 'small',
    },
    {
      key: 'delete',
      label: '删除',
      type: 'danger',
      event: 'delete',
      size: 'small',
    },
  ]

  // API 调用包装
  const api = {
    // 【关键修改4】: 修改 getList 方法以处理日期范围
    async getList(params) {
      try {
        const apiParams = { ...params }
        // 处理日期范围参数
        if (apiParams.created_at_range && apiParams.created_at_range.length === 2) {
          apiParams.created_at_start = apiParams.created_at_range[0]
          apiParams.created_at_end = apiParams.created_at_range[1]
        }
        delete apiParams.created_at_range // 删除临时字段

        const response = await userApi.getUserList(apiParams)

        // apiUtils.js已经返回标准格式{records, total}，直接返回
        return response
      } catch (error) {
        console.error('获取用户列表失败:', error)
        ElMessage.error('获取用户列表失败')
        throw error
      }
    },

    // 创建用户 - HTTP拦截器已处理422错误显示
    async create(data) {
      const result = await userApi.createUser(data)
      return result
    },

    // 更新用户 - HTTP拦截器已处理422错误显示
    async update(id, data) {
      const result = await userApi.updateUser(id, data)
      return result
    },

    // 删除用户
    async delete(id) {
      try {
        await userApi.deleteUser(id)
        return true
      } catch (error) {
        console.error('删除用户失败:', error)
        // 检查是否是后端返回的成功消息被当作错误处理
        if (
          error.message &&
          (error.message.includes('删除成功') ||
            error.message.includes('用户删除成功') ||
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
        await userApi.batchDeleteUser(ids)
        // 移除重复的消息提示，由useCrud统一处理
        return true
      } catch (error) {
        console.error('批量删除失败:', error)
        throw error // 重新抛出错误，让useCrud处理
      }
    },

    // 更新状态
    async updateStatus(id, status) {
      try {
        await userApi.updateUserStatus(id, status)
        ElMessage.success('状态更新成功')
        return true
      } catch (error) {
        console.error('状态更新失败:', error)
        ElMessage.error('状态更新失败')
        return false
      }
    },

    // 重置密码
    async resetPassword(id, newPassword = '123456') {
      try {
        await userApi.resetUserPassword(id, newPassword)
        ElMessage.success('密码重置成功')
        return true
      } catch (error) {
        console.error('密码重置失败:', error)
        ElMessage.error('密码重置失败')
        return false
      }
    },

    // 导出数据
    async export(params) {
      try {
        // 调用后端导出API
        await userApi.exportUsers(params)
        ElMessage.success('导出请求已发送，文件将自动下载')
        return true
      } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败')
        return false
      }
    },
  }

  // 状态变更确认
  const handleBeforeStatusChange = async (user) => {
    const newStatus = user.status === 'active' ? 'disabled' : 'active'
    const newStatusText = newStatus === 'active' ? '启用' : '禁用'

    try {
      await ElMessageBox.confirm(
        `确定要"${newStatusText}"用户 [${user.full_name}] 吗？`,
        '状态变更确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        },
      )

      return await api.updateStatus(user.id, newStatus)
    } catch (error) {
      if (error !== 'cancel') {
        console.error('状态变更失败:', error)
      }
      return false
    }
  }

  // 重置密码确认
  const handleResetPassword = async (user) => {
    try {
      await ElMessageBox.confirm(`确定要重置用户 [${user.full_name}] 的密码吗？`, '重置密码确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })

      return await api.resetPassword(user.id)
    } catch (error) {
      if (error !== 'cancel') {
        console.error('重置密码失败:', error)
      }
      return false
    }
  }

  // 动态配置查询字段选项
  const dynamicQueryFields = computed(() => {
    return queryFields.map((field) => {
      if (field.prop === 'role') {
        return {
          ...field,
          options: Array.isArray(roleOptions.value)
            ? roleOptions.value.map((role) => ({
                label: role.role_name || role.label,
                value: role.id || role.value,
              }))
            : [],
        }
      }

      return field
    })
  })

  // 初始化数据
  const initializeData = async () => {
    try {
      // 确保全局数据已加载
      await globalStore.fetchRoleOptions()

      // 角色选项由计算属性实时读取，无需手动赋值
      if (!globalStore.roleOptions || globalStore.roleOptions.length === 0) {
        console.warn('用户管理 - 角色选项为空')
      }
    } catch (error) {
      console.error('初始化用户管理数据失败:', error)
    }
  }

  // 自定义操作处理
  const handleCustomAction = ({ type, action, data }) => {
    switch (action) {
      case 'resetPassword':
        return handleResetPassword(data)
      default:
        return Promise.resolve(false)
    }
  }

  return {
    // 响应式数据
    crudTableRef,
    roleOptions,

    // 配置
    initialQueryParams,
    queryFields,
    dynamicQueryFields,
    tableColumns,
    permissions,
    headerActionConfig,
    rowActionConfig,

    // API 调用
    api,

    // 方法
    initializeData,
    handleCustomAction,
    handleBeforeStatusChange,
    handleResetPassword,
  }
}
