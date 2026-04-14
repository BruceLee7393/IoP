// src/stores/globalStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getRoleOptions } from '@/api/role'
import { getAllPermissions, getCurrentUserPermissions } from '@/api/permission'
import { handleDataFetchError } from '@/utils/errorHandler'
import { buildPermissionTree } from '@/utils/permissionGrouper'

// 前端树构建逻辑已移除，现在直接使用后端API返回的树形数据

export const useGlobalStore = defineStore('global', () => {
  // State
  const roleOptions = ref([])
  const allPermissions = ref([])
  const currentUserPermissions = ref([])
  const navigationMenu = ref([]) // 动态导航菜单
  const hasFetchedRoles = ref(false)
  const hasFetchedPermissions = ref(false)
  const hasFetchedUserPermissions = ref(false)
  const hasFetchedNavigationMenu = ref(false)

  // 数据最后更新时间
  const lastFetchTime = ref({
    roles: null,
    permissions: null,
    userPermissions: null,
    navigationMenu: null,
  })

  // 缓存过期时间（毫秒）- 可配置
  const CACHE_EXPIRE_TIME = {
    roles: 10 * 60 * 1000, // 角色数据：10分钟
    permissions: 30 * 60 * 1000, // 权限数据：30分钟
    userPermissions: 10 * 60 * 1000, // 用户权限：10分钟
    navigationMenu: 10 * 60 * 1000, // 导航菜单：10分钟
  }

  // 检查缓存是否过期
  const isCacheExpired = (dataType) => {
    const lastTime = lastFetchTime.value[dataType]
    if (!lastTime) return true

    const now = Date.now()
    const expireTime = CACHE_EXPIRE_TIME[dataType]
    return now - lastTime > expireTime
  }

  // Actions

  async function fetchRoleOptions(forceRefresh = false) {
    if (hasFetchedRoles.value && !forceRefresh && !isCacheExpired('roles')) {
      return
    }
    try {
      const res = await getRoleOptions()
      // console.log('从API获取到的角色数据:', res.data)
      // 确保返回的是数组格式，getRoleOptions现在直接返回角色数组
      roleOptions.value = Array.isArray(res.data) ? res.data : []
      // console.log('设置的角色选项:', roleOptions.value)
      hasFetchedRoles.value = true
      lastFetchTime.value.roles = Date.now()
    } catch (error) {
      roleOptions.value = handleDataFetchError(error, '角色数据', [])
    }
  }

  // 监听全局实体变更事件，自动刷新相关选项
  if (typeof window !== 'undefined') {
    window.addEventListener('entity-changed', async (e) => {
      const name = e?.detail?.entityName?.toLowerCase?.() || ''
      try {
        // 角色发生变化：刷新角色选项
        if (name.includes('角色')) {
          await fetchRoleOptions(true)
        }
        if (name.includes('role')) {
          await fetchRoleOptions(true)
        }


        // 权限变化
        if (name.includes('权限') || name.includes('permission')) {
          await fetchAllPermissions(true)
          await fetchCurrentUserPermissions(true)
          await fetchNavigationMenu(true) // 权限变更时刷新导航菜单
        }
      } catch (err) {
        // 静默失败
      }
    })
  }





  // 获取所有权限列表
  async function fetchAllPermissions(forceRefresh = false) {
    if (hasFetchedPermissions.value && !forceRefresh && !isCacheExpired('permissions')) {
      return
    }
    try {
      const res = await getAllPermissions()
      allPermissions.value = Array.isArray(res) ? res : []
      hasFetchedPermissions.value = true
      lastFetchTime.value.permissions = Date.now()
    } catch (error) {
      allPermissions.value = handleDataFetchError(error, '权限数据', [])
    }
  }

  // 获取当前用户权限
  async function fetchCurrentUserPermissions(forceRefresh = false) {
    if (hasFetchedUserPermissions.value && !forceRefresh && !isCacheExpired('userPermissions')) {
      return
    }
    try {
      const res = await getCurrentUserPermissions()
      currentUserPermissions.value = Array.isArray(res) ? res : []
      hasFetchedUserPermissions.value = true
      lastFetchTime.value.userPermissions = Date.now()
    } catch (error) {
      currentUserPermissions.value = handleDataFetchError(error, '用户权限数据', [])
    }
  }

  // 构建导航菜单
  async function fetchNavigationMenu(forceRefresh = false) {
    if (hasFetchedNavigationMenu.value && !forceRefresh && !isCacheExpired('navigationMenu')) {
      return
    }

    try {
      // 确保已获取当前用户权限
      await fetchCurrentUserPermissions(forceRefresh)

      // 基于用户权限构建导航菜单
      navigationMenu.value = buildPermissionTree(currentUserPermissions.value, {
        includeModuleNodes: false, // 导航栏：扁平结构，但保留模块信息用于分组
        onlyUserPermissions: true
      })

      hasFetchedNavigationMenu.value = true
      lastFetchTime.value.navigationMenu = Date.now()
      console.log('🎯 构建导航菜单完成:', navigationMenu.value)
    } catch (error) {
      console.error('构建导航菜单失败:', error)
      navigationMenu.value = []
    }
  }

  // 初始化所有数据
  async function initializeData() {
    await Promise.all([
      fetchRoleOptions(),
      fetchAllPermissions(),
      fetchCurrentUserPermissions(),
      fetchNavigationMenu(), // 添加导航菜单初始化
    ])
  }

  // 手动刷新所有数据
  async function refreshAllData() {
    // console.log('🔄 手动刷新所有全局数据')
    await Promise.all([
      fetchRoleOptions(true),
      fetchAllPermissions(true),
      fetchCurrentUserPermissions(true),
      fetchNavigationMenu(true),
    ])
  }

  // 刷新特定类型的数据
  async function refreshData(dataType) {
    // console.log(`🔄 手动刷新${dataType}数据`)
    switch (dataType) {
      case 'roles':
        await fetchRoleOptions(true)
        break
      case 'permissions':
        await fetchAllPermissions(true)
        break
      case 'userPermissions':
        await fetchCurrentUserPermissions(true)
        break
      case 'navigationMenu':
        await fetchNavigationMenu(true)
        break
      default:
        console.warn(`未知的数据类型: ${dataType}`)
    }
  }

  // 检查所有数据的缓存状态
  const getCacheStatus = () => {
    return {
      roles: {
        fetched: hasFetchedRoles.value,
        lastFetch: lastFetchTime.value.roles,
        expired: isCacheExpired('roles'),
      },

      permissions: {
        fetched: hasFetchedPermissions.value,
        lastFetch: lastFetchTime.value.permissions,
        expired: isCacheExpired('permissions'),
      },
      userPermissions: {
        fetched: hasFetchedUserPermissions.value,
        lastFetch: lastFetchTime.value.userPermissions,
        expired: isCacheExpired('userPermissions'),
      },
    }
  }

  // 重置方法
  function $reset() {
    roleOptions.value = []
    allPermissions.value = []
    currentUserPermissions.value = []
    navigationMenu.value = []
    hasFetchedRoles.value = false
    hasFetchedPermissions.value = false
    hasFetchedUserPermissions.value = false
    hasFetchedNavigationMenu.value = false
    lastFetchTime.value = {
      roles: null,
      permissions: null,
      userPermissions: null,
      navigationMenu: null,
    }
  }

  return {
    roleOptions,
    allPermissions,
    currentUserPermissions,
    navigationMenu,
    fetchRoleOptions,
    fetchAllPermissions,
    fetchCurrentUserPermissions,
    fetchNavigationMenu,
    initializeData,
    refreshAllData,
    refreshData,
    getCacheStatus,
    $reset,
  }
})
