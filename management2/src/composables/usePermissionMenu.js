// src/composables/usePermissionMenu.js
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export function usePermissionMenu() {
  const router = useRouter()
  const authStore = useAuthStore()

  // 权限菜单映射表
  const permissionMenuMap = ref({
    // 系统管理
    system_view: { path: 'system', requiresParent: false },
    user_manage: { path: 'system/user', requiresParent: 'system_view' },
    role_manage: { path: 'system/role', requiresParent: 'system_view' },

    // 基础管理
    basic_view: { path: 'basic', requiresParent: false },
    org_manage: { path: 'basic/organization', requiresParent: 'basic_view' },
    device_manage: { path: 'basic/device', requiresParent: 'basic_view' },

    // 升级管理
    upgrade_view: { path: 'upgrade', requiresParent: false },
    firmware_manage: { path: 'upgrade/firmware', requiresParent: 'upgrade_view' },
    upgrade_task: { path: 'upgrade/task', requiresParent: 'upgrade_view' },
    upgrade_record: { path: 'upgrade/record', requiresParent: 'upgrade_view' },

    // 点钞查询
    transaction_view: { path: 'transaction', requiresParent: false },
    transaction_query: { path: 'transaction/query', requiresParent: 'transaction_view' },
    transaction_analysis: { path: 'transaction/analysis', requiresParent: 'transaction_view' },

    // 设备日志
    device_log: { path: 'log', requiresParent: false },
  })

  // 智能权限推断
  const inferPermissions = (userPermissions) => {
    const inferredPermissions = new Set(userPermissions)

    // 如果有子权限，自动推断父权限
    userPermissions.forEach((permission) => {
      const config = permissionMenuMap.value[permission]
      if (config && config.requiresParent) {
        inferredPermissions.add(config.requiresParent)
      }
    })

    return Array.from(inferredPermissions)
  }

  // 构建权限菜单树
  const buildPermissionMenuTree = (permissions) => {
    const inferredPermissions = inferPermissions(permissions)
    const allRoutes = router.getRoutes()
    const mainRoute = allRoutes.find((route) => route.path === '/')

    if (!mainRoute || !mainRoute.children) return []

    const filterRoutes = (routes) => {
      return routes.filter((route) => {
        // 检查是否有对应的权限
        const hasPermission = checkRoutePermission(route, inferredPermissions)

        if (!hasPermission) return false

        // 递归处理子路由
        if (route.children && route.children.length > 0) {
          route.children = filterRoutes(route.children)
          // 如果所有子路由都被过滤掉，则父路由也不显示
          return route.children.length > 0
        }

        return true
      })
    }

    return filterRoutes(mainRoute.children)
  }

  // 检查路由权限
  const checkRoutePermission = (route, permissions) => {
    // 如果路由没有权限要求，默认允许访问
    if (!route.meta || !route.meta.permission) {
      return true
    }

    const requiredPermission = route.meta.permission

    // 支持多种权限格式
    if (Array.isArray(requiredPermission)) {
      // 数组格式：需要满足其中任一权限
      return requiredPermission.some((perm) => permissions.includes(perm))
    } else if (typeof requiredPermission === 'string') {
      // 字符串格式：需要具体权限
      return permissions.includes(requiredPermission)
    } else if (typeof requiredPermission === 'object') {
      // 对象格式：支持复杂权限逻辑
      return evaluatePermissionObject(requiredPermission, permissions)
    }

    return false
  }

  // 评估复杂权限对象
  const evaluatePermissionObject = (permissionObj, userPermissions) => {
    if (permissionObj.and) {
      // 需要同时满足多个权限
      return permissionObj.and.every((perm) => userPermissions.includes(perm))
    }

    if (permissionObj.or) {
      // 需要满足其中任一权限
      return permissionObj.or.some((perm) => userPermissions.includes(perm))
    }

    if (permissionObj.not) {
      // 不能有某个权限
      return !userPermissions.includes(permissionObj.not)
    }

    return false
  }

  // 动态菜单生成
  const dynamicMenuRoutes = computed(() => {
    const userPermissions = authStore.user?.permissions || []
    return buildPermissionMenuTree(userPermissions)
  })

  // 路由守卫
  const setupRouteGuard = () => {
    router.beforeEach((to, from, next) => {
      const userPermissions = authStore.user?.permissions || []

      // 检查路由权限
      if (to.meta && to.meta.permission) {
        const hasPermission = checkRoutePermission(to, userPermissions)

        if (!hasPermission) {
          // 没有权限，重定向到首页
          next({ path: '/home' })
          return
        }
      }

      next()
    })
  }

  // 权限检查工具函数
  const hasPermission = (permission) => {
    const userPermissions = authStore.user?.permissions || []
    return userPermissions.includes(permission) || userPermissions.includes('all')
  }

  const hasAnyPermission = (permissions) => {
    const userPermissions = authStore.user?.permissions || []
    return (
      permissions.some((perm) => userPermissions.includes(perm)) || userPermissions.includes('all')
    )
  }

  const hasAllPermissions = (permissions) => {
    const userPermissions = authStore.user?.permissions || []
    return (
      permissions.every((perm) => userPermissions.includes(perm)) || userPermissions.includes('all')
    )
  }

  // 菜单权限实时更新
  const refreshMenuPermissions = async () => {
    try {
      // 重新获取用户权限
      await authStore.refreshUserInfo()

      // 检查当前路由是否还有权限
      const currentRoute = router.currentRoute.value
      const userPermissions = authStore.user?.permissions || []

      if (currentRoute.meta && currentRoute.meta.permission) {
        const hasPermission = checkRoutePermission(currentRoute, userPermissions)

        if (!hasPermission) {
          // 当前页面没有权限，跳转到首页
          router.push('/home')
        }
      }
    } catch (error) {
      console.error('刷新菜单权限失败:', error)
    }
  }

  // 监听权限变化
  watch(
    () => authStore.user?.permissions,
    (newPermissions, oldPermissions) => {
      if (JSON.stringify(newPermissions) !== JSON.stringify(oldPermissions)) {
        console.log('用户权限发生变化，重新构建菜单')
        // 权限变化时可以在这里做一些处理
      }
    },
    { deep: true },
  )

  return {
    dynamicMenuRoutes,
    setupRouteGuard,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    refreshMenuPermissions,
    checkRoutePermission,
    buildPermissionMenuTree,
  }
}
