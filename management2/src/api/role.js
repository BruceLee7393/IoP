// src/api/role.js
import { request } from '@/utils/http'
import { createGetListMethod, createExportMethod } from '@/utils/apiUtils'

// 字段映射配置
const ROLE_FIELD_MAPPING = {
  roleCode: 'role_code',
  roleName: 'role_name',
  status: 'status',
  page: 'page',
  pageSize: 'per_page',
  sortBy: 'sort_by',
  order: 'sort_order',
}

// 获取角色列表 - 使用通用方法
export const getRoleList = createGetListMethod('/roles', ROLE_FIELD_MAPPING)

// 导出角色数据 - 使用通用方法
export const exportRoles = createExportMethod(
  '/roles/export',
  ROLE_FIELD_MAPPING,
  'role_export.xlsx',
  '角色数据导出',
)

// 创建角色 - HTTP拦截器已处理错误响应
export const createRole = async (data) => {
  const response = await request.post('/roles', data)
  return { data: response.data }
}

// 更新角色信息 - HTTP拦截器已处理错误响应
export const updateRole = async (id, data) => {
  const response = await request.put(`/roles/${id}`, data)
  return { data: response.data }
}

// 删除角色 - HTTP拦截器已处理错误响应
export const deleteRole = async (id) => {
  const response = await request.delete(`/roles/${id}`)
  return { data: response.data }
}

// 批量删除角色 - 保留参数验证
export const batchDeleteRole = async (ids) => {
  // 验证参数
  if (!ids || !Array.isArray(ids) || ids.length === 0) {
    throw new Error('角色ID列表不能为空')
  }

  // 后端期望接收的参数名是 role_ids
  const requestData = { role_ids: ids }
  const response = await request.delete('/roles/batch-delete', {
    data: requestData,
  })
  return { data: response.data }
}

// 获取全部权限（树形）- HTTP拦截器已处理响应格式
export const getPermissions = async () => {
  const response = await request.get('/permissions')
  // console.log('getPermissions - API响应:', response)
  return { data: response.data }
}

// 获取角色已分配权限 - HTTP拦截器已处理响应格式
export const getRolePermissions = async (roleId) => {
  const response = await request.get(`/roles/${roleId}/permissions`)

  return { data: response.data }
}

// 分配权限给角色 - HTTP拦截器已处理响应格式
export const assignPermissions = async (roleId, permissionIds) => {
  const response = await request.post(`/roles/${roleId}/permissions`, { permissionIds })

  return { data: response.data }
}

// 获取角色选项（用于下拉框）- HTTP拦截器已处理响应格式
export const getRoleOptions = async () => {
  const response = await request.get('/roles', { _limit: 1000 })


  // HTTP拦截器已经处理了响应格式，直接使用
  const roles = response.data.records || response.data || []

  // 过滤掉无效数据并返回
  const validRoles = Array.isArray(roles) ? roles.filter((role) => role && role.id) : []


  return { data: validRoles }
}



// 更新角色权限
export const updatePermissions = async (roleId, permissionIds) => {
  try {
    const response = await assignPermissions(roleId, permissionIds)
    return response
  } catch (error) {
    console.error('Error in updatePermissions:', error)
    throw error
  }
}
