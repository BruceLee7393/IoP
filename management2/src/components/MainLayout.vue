<template>
  <div class="modern-layout" :class="{ 'sidebar-collapsed': isCollapse }">
    <aside class="modern-sidebar" :class="{ collapsed: isCollapse }">
      <div class="logo-section">
        <div class="logo-container">
          <div class="logo-icon">
            <img src="../assets/images/logo.png" alt="产品管理系统" class="logo-svg" />
          </div>

          <transition name="logo-text">
            <div v-show="!isCollapse" class="logo-text">
              <span class="logo-title">产品管理系统</span>
          
            </div>
          </transition>
        </div>
      </div>

      <nav class="navigation-menu">
        <el-scrollbar class="menu-scrollbar">
          <el-menu
            :default-active="activeMenu"
            :collapse="isCollapse"
            :collapse-transition="false"
            router
          >
            <MenuItem
              v-for="route in menuRoutes"
              :key="route.path"
              :item="route"
              :collapsed="isCollapse"
            />
          </el-menu>
        </el-scrollbar>
      </nav>

      <div class="sidebar-footer">
        <div class="collapse-trigger" @click="isCollapse = !isCollapse">
          <div class="collapse-icon">
            <el-icon><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
          </div>
          <transition name="collapse-text">
            <span v-show="!isCollapse" class="collapse-text">收起菜单</span>
          </transition>
        </div>
      </div>
    </aside>

    <div class="main-container">
      <header class="modern-header">
        <div class="header-content">
          <div class="header-left">
            <button
              class="menu-toggle-btn"
              @click="toggleSidebar"
              :title="isCollapse ? '展开菜单' : '收起菜单'"
            >
              <el-icon>
                <Fold v-if="!isCollapse" />
                <Expand v-else />
              </el-icon>
            </button>

            <nav class="breadcrumb-nav">
              <ol class="breadcrumb-list">
                <li v-for="(item, index) in breadcrumbs" :key="item.path" class="breadcrumb-item">
                  <router-link
                    v-if="index < breadcrumbs.length - 1"
                    :to="item.path"
                    class="breadcrumb-link"
                  >
                    {{ item.meta.title }}
                  </router-link>
                  <span v-else class="breadcrumb-current">{{ item.meta.title }}</span>
                  <span v-if="index < breadcrumbs.length - 1" class="breadcrumb-separator">
                    <el-icon><ArrowRight /></el-icon>
                  </span>
                </li>
              </ol>
            </nav>
          </div>

          <div class="header-right">
            <el-dropdown class="user-dropdown" trigger="click" @command="handleCommand">
              <div class="user-profile">
                <div class="user-avatar">
                  <img src="../assets/images/tx.png" alt="用户头像" />
                </div>
                <div class="user-info">
                  <div class="user-name">{{ getUserDisplayName }}</div>
                  <div class="user-role" v-if="getUserRole">{{ getUserRole }}</div>
                </div>
                <div class="dropdown-arrow">
                  <el-icon><ArrowDown /></el-icon>
                </div>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="user-dropdown-menu">
                  <el-dropdown-item command="profile" class="dropdown-item">
                    <el-icon><User /></el-icon>
                    <span>个人中心</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" class="dropdown-item" divided>
                    <el-icon><SwitchButton /></el-icon>
                    <span>退出登录</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </header>

      <main class="main-content">
        <div class="content-wrapper">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
// 导入 Header 和布局中直接用到的图标
import { ArrowDown, ArrowRight, Fold, Expand, User, SwitchButton } from '@element-plus/icons-vue'
// 引入创建的递归菜单组件
import MenuItem from './MenuItem.vue'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

const isCollapse = ref(false)
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const permissionStore = usePermissionStore()

// 确保权限系统已初始化
// 权限初始化在应用启动时已处理，这里无需再次初始化
onMounted(() => {})

// 【修复警告1】定义 activeMenu 计算属性
const activeMenu = computed(() => route.path)

// 用户显示名称
const getUserDisplayName = computed(() => {
  const user = authStore.user
  if (!user) return '未登录'
  // 优先显示 full_name，其次 account，最后兜底为“用户”
  return user.full_name || user.account || '用户'
})

// 用户角色显示（仅显示角色名称）
const getUserRole = computed(() => {
  const user = authStore.user
  if (!user) return null

  // 直接平铺在 user 上的可能字段
  const directName =
    user.roleName ||
    user.role_name ||
    user.roleLabel ||
    user.roleTitle ||
    user['role name']
  if (typeof directName === 'string' && directName.trim()) return directName

  // 可能存在的嵌套 role 信息（对象或字符串）
  const rawRole = user.role || user.role_info || user.roleInfo

  // 如果是字符串，优先尝试当成 JSON 解析；解析失败则按纯名称使用
  if (typeof rawRole === 'string') {
    try {
      const parsed = JSON.parse(rawRole)
      const parsedName =
        parsed?.role_name || parsed?.roleName || parsed?.name || parsed?.['role name'] || parsed?.label
      if (typeof parsedName === 'string' && parsedName.trim()) return parsedName
    } catch (_) {
      if (rawRole.trim()) return rawRole
    }
  }

  // 如果是对象，从常见字段中提取名称
  if (rawRole && typeof rawRole === 'object') {
    const objName =
      rawRole.role_name || rawRole.roleName || rawRole.name || rawRole['role name'] || rawRole.label
    if (typeof objName === 'string' && objName.trim()) return objName
  }

  return null
})

// 动态构建导航菜单
const menuRoutes = computed(() => {
  return permissionStore.navigationMenu || []
})

// 面包屑逻
const breadcrumbs = computed(() => {
  return route.matched.filter((item) => item.meta && item.meta.title && item.path !== '/')
})

const handleCommand = (command) => {
  if (command === 'logout') {
    handleLogout()
  } else if (command === 'profile') {
    router.push({ name: 'Profile' })
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('您确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

        // 调用authStore的登出方法
    await authStore.logout()
    ElMessage.success('已退出登录')

    // 跳转到登录页
    router.push('/login')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('登出失败:', error)
      ElMessage.error('登出失败，请稍后重试')
    }
  }
}

// 切换侧边栏状态
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<style scoped>
/* ========================================
   MainLayout 组件样式
   使用设计系统中的样式类
   ======================================== */



/* 确保滚动条样式应用 */
.menu-scrollbar {
  height: 100%;
}

.menu-scrollbar .el-scrollbar__wrap {
  overflow-x: hidden;
}

/* 确保侧边栏收起时的样式 */
.modern-sidebar.collapsed .el-menu-item,
.modern-sidebar.collapsed .el-sub-menu__title {
  padding: 0;
  text-align: center;
}


</style>
