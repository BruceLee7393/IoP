import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 引入中文语言包
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// 注销掉默认的 mock 服务
// import './mock' // 当需要时启用Mock数据，正式环境请关闭Mock

import './assets/main.css'

import { createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

// 应用启动前主动初始化认证与权限，确保动态路由在首次导航前就绪
;(async () => {
  try {
    const authStore = useAuthStore()
    const permissionStore = usePermissionStore()

    const inited = await authStore.initAuth()
    if (inited && authStore.isLoggedIn && !permissionStore.initialized) {
      await permissionStore.initializePermissions()
    }
  } catch (e) {
    // 初始化失败时不阻塞应用挂载，由路由守卫兜底
    // console.error('App bootstrap failed:', e)
  } finally {
    app.use(router)
    app.use(ElementPlus, {
      locale: zhCn, // 设置中文
    })
    app.mount('#app')
  }
})()
