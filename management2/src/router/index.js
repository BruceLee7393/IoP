import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

import MainLayout from '../components/MainLayout.vue'

/**
 * 基础路由配置
 * 只包含不需要权限验证的公共路由，如登录页、404页等
 * 所有业务路由将根据用户权限动态添加
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Layout',
      component: MainLayout,
      children: [
        // 首页 - 展示图片
        {
          path: 'home',
          name: 'Home',
          component: () => import('../views/home/HomeView.vue'),
          meta: { title: '首页' },
        },
        // 个人中心 - 所有用户都可以访问
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('../views/profile/PersonalCenterView.vue'),
          meta: { title: '个人中心', hidden: true },
        },
      ],
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/login/LoginView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ],
})

// 不需要登录的白名单页面（已由API层区分，不在前端路由使用）

// 全局前置守卫 - 简化版本
router.beforeEach(async (to, from, next) => {
  console.log('🛡️ 路由守卫:', from.path, '->', to.path)

  const authStore = useAuthStore()
  const permissionStore = usePermissionStore()



  // 生产模式：正常路由守卫逻辑
  // 如果访问登录页，直接放行
  if (to.path === '/login') {
    console.log('✅ 访问登录页，直接放行')
    next()
    return
  }

  // 检查认证状态是否已初始化
  if (!authStore.initialized) {
    console.log('🔄 认证状态未初始化，开始初始化...')
    const initResult = await authStore.initAuth()
    // 初始化失败时，不立即强跳；允许进入页面展示“离线/服务不可用”状态。
    if (!initResult) {
      console.log('❌ 认证状态初始化失败，重定向到登录页')
      next('/login')
      return
    }
    console.log('✅ 认证状态初始化成功')
  }

  // 检查登录状态
  if (!authStore.isLoggedIn) {
    console.log('❌ 用户未登录，重定向到登录页')
    next('/login')
    return
  }

  // 检查权限系统是否已初始化
  if (!permissionStore.initialized) {
    console.log('🔄 权限系统未初始化，开始初始化...')
    try {
      await permissionStore.initializePermissions()
      console.log('✅ 权限系统初始化完成，动态路由已注册')
      // 初始化完成后：若在根路径，直接定向到 /home；否则保持原目标
      if (to.path === '/') {
        next({ path: '/home', replace: true })
      } else {
        next({ ...to, replace: true })
      }
    } catch (error) {
      console.error('❌ 权限系统初始化失败:', error)
      await authStore.logout()
      next('/login')
    }
  } else {
    console.log('✅ 用户已登录且权限已初始化，允许访问:', to.path)
    // 守卫兜底：若访问根路径，始终跳转到 /home，避免空白页
    if (to.path === '/') {
      next('/home')
    } else {
      next()
    }
  }
})


// 全局后置守卫
router.afterEach((to) => {
  // 设置页面标题
  if (to.meta && to.meta.title) {
    document.title = `${to.meta.title} - 产品管理系统`
  } else {
    document.title = '产品管理系统'
  }
})

export default router
