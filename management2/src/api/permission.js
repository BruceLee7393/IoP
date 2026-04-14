// src/api/permission.js
import http from '@/utils/http'

/**
 * 获取所有权限列表
 * @returns {Promise} 权限列表
 */
export const getAllPermissions = () => {
  return http.get('/roles/permissions')
}

/**
 * 获取当前用户权限
 * @returns {Promise} 当前用户权限列表
 */
export const getCurrentUserPermissions = () => {
  return http.get('/roles/permissions/current')
}

/**
 * 获取指定角色的权限
 * @param {string} roleId 角色ID
 * @returns {Promise} 角色权限列表
 */
export const getRolePermissions = (roleId) => {
  return http.get(`/roles/permissions/${roleId}`)
}

/**
 * 批量添加角色权限
 * @param {string} roleId 角色ID
 * @param {Array<string>} permissionIds 权限ID列表
 * @returns {Promise} 添加结果
 */
export const addRolePermissions = (roleId, permissionIds) => {
  return http.post(`/roles/permissions/${roleId}/batch-add`, {
    permission_ids: permissionIds
  })
}

/**
 * 批量删除角色权限
 * @param {string} roleId 角色ID
 * @param {Array<string>} permissionIds 权限ID列表
 * @returns {Promise} 删除结果
 */
export const removeRolePermissions = (roleId, permissionIds) => {
  return http.delete(`/roles/permissions/${roleId}/batch-delete`, {
    data: {
      permission_ids: permissionIds
    }
  })
}

