// src/stores/permission.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getAllPermissions, getCurrentUserPermissions } from '@/api/permission'
import { buildPermissionTree } from '@/utils/permissionGrouper'
import router from '@/router'


/**
 * 权限管理 Store
 * 负责权限数据管理、动态路由注册、权限验证等核心功能
 */
export const usePermissionStore = defineStore('permission', () => {
  // ==================== 状态管理 ====================

  /** 所有系统权限列表 */
  const allPermissions = ref([])

  /** 当前用户拥有的权限列表 */
  const userPermissions = ref([])

  /** 当前用户权限代码集合（用于快速查找） */
  const userPermissionCodes = computed(() => {
    return new Set(userPermissions.value.map(p => p.permission_code))
  })

  /** 动态路由是否已注册 */
  const routesRegistered = ref(false)

  /** 权限数据是否已初始化 */
  const initialized = ref(false)

  /** 动态导航菜单 */
  const navigationMenu = computed(() => {
    // 即使权限为空也调用构建函数，让其自动注入“首页”
    return buildPermissionTree(userPermissions.value || [], {
      includeModuleNodes: true, // 导航菜单需要模块节点（如基础管理）
      onlyUserPermissions: true
    })
  })

  // ==================== 权限验证方法 ====================

  /**
   * 检查用户是否拥有指定权限
   * @param {string} permissionCode - 权限代码
   * @returns {boolean}
   */
  const hasPermission = (permissionCode) => {
    return userPermissionCodes.value.has(permissionCode)
  }

  /**
   * 检查用户是否拥有指定权限中的任意一个
   * @param {string[]} permissionCodes - 权限代码数组
   * @returns {boolean}
   */
  const hasAnyPermission = (permissionCodes) => {
    return permissionCodes.some(code => hasPermission(code))
  }

  /**
   * 检查用户是否拥有指定的所有权限
   * @param {string[]} permissionCodes - 权限代码数组
   * @returns {boolean}
   */
  const hasAllPermissions = (permissionCodes) => {
    return permissionCodes.every(code => hasPermission(code))
  }

  // ==================== 数据获取方法 ====================

  /**
   * 获取所有系统权限
   */
  const fetchAllPermissions = async () => {
    try {
      console.log('🔄 获取所有系统权限...')
      const response = await getAllPermissions()

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
      console.log('✅ 获取系统权限成功:', permissions.length, '项')
      return permissions
    } catch (error) {
      console.error('❌ 获取系统权限失败:', error)
      throw error
    }
  }

    /**
   * 获取当前用户权限
   */
  const fetchUserPermissions = async () => {
    try {
      console.log(' 获取当前用户权限...')

      // 正常获取权限
      const response = await getCurrentUserPermissions()
      console.log(' 原始权限API响应:', response)

      // 处理不同的响应格式
      let permissions = []
      if (Array.isArray(response)) {
        permissions = response
      } else if (response && response.code === 0 && Array.isArray(response.data)) {
        permissions = response.data
      } else if (response && Array.isArray(response.data)) {
        permissions = response.data
      }

      userPermissions.value = permissions
      console.log(' 获取用户权限成功:', permissions.length, '项')
      console.log(' 权限代码列表:', permissions.map(p => p.permission_code))
      return permissions
    } catch (error) {
      console.error(' 获取用户权限失败:', error)

      // 失败时返回空数组
      userPermissions.value = []
      return []
    }
  }

  // ==================== 动态路由管理 ====================

  /**
   * 根据权限代码获取路由配置
   */
  const getRouteConfig = (permissionCode) => {
    const routeConfigs = {
      'Home': {
        path: '/home',
        name: 'Home',
        component: () => import('../views/home/HomeView.vue'),
        meta: { title: '首页',icon: 'DataLine', permission: 'Home' }
      },

      'UserManagement': {
        path: '/sys_manage/user',
        name: 'UserManagement',
        component: () => import('../views/sys_manage/UserView.vue'),
        meta: { title: '用户管理', icon: 'User', permission: 'UserManagement' }
      },
      'RoleManagement': {
        path: '/sys_manage/role',
        name: 'RoleManagement',
        component: () => import('../views/sys_manage/RoleView.vue'),
        meta: { title: '角色管理', icon: 'UserFilled', permission: 'RoleManagement' }
      },


      'OrderManagement': {
        path: '/order',
        name: 'OrderManagement',
        component: () => import('../views/order/OrderView.vue'),
        meta: { title: '订单管理', icon: 'Document', permission: 'OrderManagement' }
      },

      // 订单子路由
      'OrderDetail': {
        path: '/order/detail/:id',
        name: 'OrderDetail',
        component: () => import('../views/order/OrderDetailView.vue'),
        meta: { title: '订单详情', hidden: true, permission: 'OrderManagement' }
      },
      // 'OrderAdd': {
      //   path: '/order/add',
      //   name: 'OrderAdd',
      //   component: () => import('../views/order/OrderAddView.vue'),
      //   meta: { title: '新增订单', hidden: true, permission: 'OrderManagement' }
      // },
      // 'OrderEdit': {
      //   path: '/order/edit/:id',
      //   name: 'OrderEdit',
      //   component: () => import('../views/order/OrderEditView.vue'),
      //   meta: { title: '编辑订单', hidden: true, permission: 'OrderManagement' }
      // }
    }

    return routeConfigs[permissionCode]
  }

  /**
   * 注册动态路由
   */
  const registerDynamicRoutes = () => {
    if (routesRegistered.value) {
      console.log('⚠️ 动态路由已注册，跳过重复注册')
      return
    }

    console.log('🔄 开始注册动态路由...')

    // 获取扩展后的权限列表（包括虚拟权限）
    const expandedPermissions = []

    // 先添加真实权限
    expandedPermissions.push(...userPermissions.value)

    // 添加权限扩展逻辑
    const userPermissionCodes = userPermissions.value.map(p => p.permission_code)

    // 点钞管理权限扩展
    if (userPermissionCodes.includes('BanknoteManagement')) {
      console.log('🔍 检测到点钞管理权限，开始扩展虚拟权限...')
      const expansionPerms = ['BanknoteByInstitution', 'BanknoteByDevice', 'BanknoteByTime']
      expansionPerms.forEach(expandedPerm => {
        if (!userPermissionCodes.includes(expandedPerm)) {
          const virtualPerm = {
            id: `virtual-${expandedPerm}`,
            permission_code: expandedPerm,
            permission_name: expandedPerm
          }
          expandedPermissions.push(virtualPerm)
          console.log('✅ 添加虚拟权限:', expandedPerm)
        } else {
          console.log('⚠️ 权限已存在，跳过:', expandedPerm)
        }
      })
    } else {
      console.log('❌ 用户没有点钞管理权限，跳过扩展')
    }

    // 订单管理权限扩展
    if (userPermissionCodes.includes('OrderManagement')) {
      console.log('🔍 检测到订单管理权限，开始扩展子路由权限...')
      const orderSubRoutes = ['OrderDetail', 'OrderAdd', 'OrderEdit']
      orderSubRoutes.forEach(subRoute => {
        if (!userPermissionCodes.includes(subRoute)) {
          const virtualPerm = {
            id: `virtual-${subRoute}`,
            permission_code: subRoute,
            permission_name: subRoute
          }
          expandedPermissions.push(virtualPerm)
          console.log('✅ 添加订单子路由权限:', subRoute)
        }
      })
    }

    // 为所有用户添加首页权限
    if (!userPermissionCodes.includes('Home')) {
      expandedPermissions.unshift({
        id: 'virtual-home',
        permission_code: 'Home',
        permission_name: '首页'
      })
    }

    // 为每个权限（包括扩展权限）注册对应的路由
    console.log('🔍 准备注册路由的权限列表:', expandedPermissions.map(p => p.permission_code))

    expandedPermissions.forEach(permission => {
      console.log('🔄 处理权限:', permission.permission_code)
      const routeConfig = getRouteConfig(permission.permission_code)
      if (routeConfig) {
        try {
          // 所有路由都添加到Layout下，包括首页
          router.addRoute('Layout', routeConfig)
          console.log('✅ 注册路由:', routeConfig.name, routeConfig.path)
        } catch (error) {
          console.error('❌ 注册路由失败:', routeConfig.name, error)
        }
      } else {
        console.warn('⚠️ 未找到权限对应的路由配置:', permission.permission_code)
      }
    })

    // 统一根路径重定向：全部跳转到 Home
    // 先移除可能存在的旧重定向路由，避免重复与冲突
    if (router.hasRoute('home-redirect')) {
      router.removeRoute('home-redirect')
    }
    if (router.hasRoute('default-redirect')) {
      router.removeRoute('default-redirect')
    }
    const redirectTarget = '/home'
    router.addRoute('Layout', {
      path: '',
      redirect: redirectTarget,
      name: 'root-redirect'
    })
    console.log(`✅ 添加根路径重定向: / -> ${redirectTarget}`)

    // 输出所有已注册的路由用于调试（放在最后，包含重定向）
    console.log('🔍 当前所有注册的路由:', router.getRoutes().map(r => ({ name: r.name, path: r.path })))

    routesRegistered.value = true
    console.log('✅ 动态路由注册完成')
  }

  /**
   * 清除动态路由（用于用户登出）
   */
  const clearDynamicRoutes = () => {
    console.log('🔄 清除动态路由...')

    // 移除所有业务路由，只保留基础路由（登录、404等）
    userPermissions.value.forEach(permission => {
      const routeConfig = getRouteConfig(permission.permission_code)
      if (routeConfig && router.hasRoute(routeConfig.name)) {
        router.removeRoute(routeConfig.name)
        console.log(' 移除路由:', routeConfig.name)
      }
    })

    routesRegistered.value = false
    console.log(' 动态路由清除完成')
  }

  // ==================== 初始化方法 ====================

  /**
   * 初始化权限系统
   */
  const initializePermissions = async () => {
    if (initialized.value) {
      console.log(' 权限系统已初始化，跳过重复初始化')
      return
    }

    try {
      console.log('开始初始化权限系统...')

      // 1. 获取用户权限
      await fetchUserPermissions()

      // 2. 注册动态路由
      registerDynamicRoutes()

      // 3. 标记为已初始化
      initialized.value = true

      console.log(' 权限系统初始化完成')
    } catch (error) {
      console.error(' 权限系统初始化失败:', error)
      throw error
    }
  }

  /**
   * 重置权限系统（用于用户登出）
   */
  const resetPermissions = () => {
    console.log('🔄 重置权限系统...')

    // 清除动态路由
    clearDynamicRoutes()

    // 清除权限数据
    allPermissions.value = []
    userPermissions.value = []
    initialized.value = false

    console.log('权限系统重置完成')
  }

  /**
   * 刷新权限数据（用于权限变更后）
   */
  const refreshPermissions = async () => {
    console.log(' 刷新权限数据...')

    try {
      // 清除现有路由
      clearDynamicRoutes()

      // 重新获取权限并注册路由
      await fetchUserPermissions()
      registerDynamicRoutes()

      console.log(' 权限数据刷新完成')
    } catch (error) {
      console.error('权限数据刷新失败:', error)
      throw error
    }
  }

  // ==================== 返回公共接口 ====================

  return {
    // 状态
    allPermissions,
    userPermissions,
    userPermissionCodes,
    navigationMenu,
    routesRegistered,
    initialized,

    // 权限验证方法
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,

    // 数据获取方法
    fetchAllPermissions,
    fetchUserPermissions,

    // 路由管理方法
    registerDynamicRoutes,
    clearDynamicRoutes,

    // 系统管理方法
    initializePermissions,
    resetPermissions,
    refreshPermissions
  }
})
