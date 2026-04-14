// src/api/user.js
import { request } from '@/utils/http'
import { createGetListMethod, createExportMethod } from '@/utils/apiUtils'

// 字段映射配置
const USER_FIELD_MAPPING = {
  username: 'account',
  account: 'account',
  fullName: 'full_name',
  contactInfo: 'contact_info',
  address: 'address',
  role: 'role_id', // 查询表单中使用的字段名
  status: 'status',
  page: 'page',
  pageSize: 'per_page',
  sortBy: 'sort_by',
  order: 'sort_order',
}

// 嵌套字段配置
const USER_NESTED_FIELDS = {
  role: ['role_name'],
}

// 获取用户列表 - 使用通用方法
export const getUserList = createGetListMethod('/users', USER_FIELD_MAPPING, USER_NESTED_FIELDS)

// 创建用户 - HTTP拦截器已处理错误响应
export const createUser = async (data) => {
  const response = await request.post('/users/register', data)
  return { data: response.data }
}

// 更新用户信息 - HTTP拦截器已处理错误响应和422错误显示
export const updateUser = async (id, data) => {
  const response = await request.put(`/users/${id}`, data)
  return { data: response.data }
}

// 删除用户 - HTTP拦截器已处理错误响应
export const deleteUser = async (id) => {
  const response = await request.delete(`/users/${id}`)
  return { data: response.data }
}

// 批量删除用户 - 保留参数验证
export const batchDeleteUser = async (ids) => {
  // 验证参数
  if (!ids || !Array.isArray(ids) || ids.length === 0) {
    throw new Error('用户ID列表不能为空')
  }

  // 后端期望接收的参数名是 user_ids
  const requestData = { user_ids: ids }
  const response = await request.delete('/users/batch-delete', {
    data: requestData,
  })

  return { data: response.data }
}

// 启用/禁用用户 - HTTP拦截器已处理错误响应
export const updateUserStatus = async (id, status) => {
  const response = await request.put(`/users/${id}`, { status })
  return { data: response.data }
}

// 重置用户密码 - HTTP拦截器已处理错误响应
export const resetUserPassword = async (id, newPassword) => {
  const response = await request.post(`/users/${id}/password-reset`, {
    newPassword,
  })
  return { data: response.data }
}

// 导出用户数据 - 使用通用方法
export const exportUsers = createExportMethod(
  '/users/export',
  USER_FIELD_MAPPING,
  'user_export.xlsx',
  '用户数据导出',
)

// 获取当前用户信息
export const getCurrentUserInfo = () => {
  return request.get('/users/me')
}

// 修改当前用户密码
export const updateCurrentUserPassword = (passwordData) => {
  return request.put('/users/me', passwordData)
}

// 修改当前用户个人资料
export const updateCurrentUserProfile = (profileData) => {
  // 仅允许白名单字段
  const payload = {
    full_name: profileData.full_name ?? '',
    contact_info: profileData.contact_info ?? '',
    address: profileData.address ?? '',
    gender: profileData.gender ?? '', // 允许值: woman | man | none | others
  }
  return request.put('/users/me', payload)
}
