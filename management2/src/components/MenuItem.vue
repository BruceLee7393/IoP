<template>
  <template v-if="!item.meta?.hidden">
    <div v-if="item.children && item.children.length > 0" class="menu-group">
      <div
        class="modern-menu-item menu-parent"
        :class="{
          active: isMenuActive(resolvePath(item.path)),
          collapsed: collapsed,
        }"
        @click="handleMenuClick"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave"
        ref="menuParentRef"
      >
        <div class="menu-item-content">
          <div class="menu-icon">
            <el-icon v-if="currentIcon">
              <component :is="currentIcon" />
            </el-icon>
          </div>
          <transition name="menu-text">
            <span v-show="!collapsed" class="menu-title">{{ item.meta?.title }}</span>
          </transition>
          <transition name="menu-arrow">
            <div v-show="!collapsed" class="menu-arrow" :class="{ expanded: isExpanded }">
              <el-icon><ArrowDown /></el-icon>
            </div>
          </transition>
        </div>
      </div>

      <transition name="submenu">
        <div v-show="!collapsed && isExpanded" class="submenu-container">
          <div
            v-for="child in item.children"
            :key="child.path"
            class="submenu-item-wrapper"
          >
            <menu-item
              :item="child"
              :base-path="resolvePath(item.path)"
              :collapsed="false"
            />
          </div>
        </div>
      </transition>

      <teleport to="body">
        <transition name="floating-menu">
          <div
            v-show="collapsed && showFloatingMenu"
            class="floating-submenu"
            :style="floatingMenuStyle"
            @mouseenter="handleFloatingMenuEnter"
            @mouseleave="handleFloatingMenuLeave"
          >
            <div class="floating-submenu-header">
              <div class="floating-menu-icon">
                <el-icon v-if="currentIcon">
                  <component :is="currentIcon" />
                </el-icon>
              </div>
              <span class="floating-menu-title">{{ item.meta?.title }}</span>
            </div>
            <div class="floating-submenu-content">
              <router-link
                v-for="child in item.children"
                :key="child.path"
                :to="resolvePath(child.path, resolvePath(item.path))"
                class="floating-submenu-item"
                :class="{ active: $route.path === resolvePath(child.path, resolvePath(item.path)) }"
                @click="hideFloatingMenu"
              >
                <div class="floating-item-icon"></div>
                <span class="floating-item-title">{{ child.meta?.title }}</span>
              </router-link>
            </div>
          </div>
        </transition>
      </teleport>
    </div>

    <router-link
      v-else
      :to="resolvePath(item.path)"
      class="modern-menu-item"
      :class="{
        active: $route.path === resolvePath(item.path),
        collapsed: collapsed,
      }"
    >
      <div class="menu-item-content">
        <div class="menu-icon">
          <el-icon v-if="currentIcon">
            <component :is="currentIcon" />
          </el-icon>
        </div>
        <transition name="menu-text">
          <span v-show="!collapsed" class="menu-title">{{ item.meta?.title }}</span>
        </transition>
      </div>
    </router-link>
  </template>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'
import { getIcon } from '@/utils/iconRegistry'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  basePath: {
    type: String,
    default: '',
  },
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const route = useRoute()
const isExpanded = ref(false)
const showFloatingMenu = ref(false)
const floatingMenuStyle = ref({})
const menuParentRef = ref(null)

// 使用 ref 来管理定时器，确保响应式和清理
const hideTimer = ref(null)
const isMouseInMenu = ref(false)
const isMouseInFloating = ref(false)

// 修复路径解析 - 直接使用菜单项的完整路径
const resolvePath = (routePath, explicitBasePath = null) => {
  // 如果路径已经是完整路径（以 / 开头），直接返回
  if (routePath && routePath.startsWith('/')) {
    return routePath
  }

  // 兼容旧的拼接逻辑
  const basePathToUse = explicitBasePath !== null ? explicitBasePath : props.basePath;
  if (!basePathToUse) {
    return `/${routePath}`
  }
  const fullPath = `${basePathToUse}/${routePath}`
  return fullPath.replace(/\/\//g, '/')
}

// 检查菜单是否激活
const isMenuActive = (path) => {
  return route.path.startsWith(path)
}

// 切换子菜单展开状态
const toggleSubmenu = () => {
  if (!props.collapsed) {
    isExpanded.value = !isExpanded.value
  }
}

// 处理菜单点击
const handleMenuClick = () => {
  if (props.collapsed) {
    // 收起状态下点击显示悬浮菜单
    showFloatingMenu.value = !showFloatingMenu.value
    if (showFloatingMenu.value) {
      calculateFloatingMenuPosition()
    }
  } else {
    // 展开状态下正常切换子菜单
    toggleSubmenu()
  }
}

// 清理定时器的通用方法
const clearHideTimer = () => {
  if (hideTimer.value) {
    clearTimeout(hideTimer.value)
    hideTimer.value = null
  }
}

// 设置延迟隐藏定时器
const setHideTimer = () => {
  clearHideTimer()
  hideTimer.value = setTimeout(() => {
    // 只有当鼠标既不在菜单项也不在悬浮菜单中时才隐藏
    if (!isMouseInMenu.value && !isMouseInFloating.value) {
      showFloatingMenu.value = false
    }
    hideTimer.value = null
  }, 300)
}

// 鼠标进入菜单项
const handleMouseEnter = () => {
  if (props.collapsed) {
    isMouseInMenu.value = true
    clearHideTimer()
    showFloatingMenu.value = true
    calculateFloatingMenuPosition()
  }
}

// 鼠标离开菜单项
const handleMouseLeave = () => {
  if (props.collapsed) {
    isMouseInMenu.value = false
    setHideTimer()
  }
}

// 鼠标进入悬浮菜单
const handleFloatingMenuEnter = () => {
  if (props.collapsed) {
    isMouseInFloating.value = true
    clearHideTimer()
  }
}

// 鼠标离开悬浮菜单
const handleFloatingMenuLeave = () => {
  if (props.collapsed) {
    isMouseInFloating.value = false
    setHideTimer()
  }
}

// 隐藏悬浮菜单
const hideFloatingMenu = () => {
  showFloatingMenu.value = false
}

// 计算悬浮菜单位置
const calculateFloatingMenuPosition = () => {
  if (!menuParentRef.value) return

  const rect = menuParentRef.value.getBoundingClientRect()

  // 动态获取侧边栏折叠宽度，避免硬编码
  const sidebarElement = document.querySelector('.sidebar')
  const sidebarWidth = sidebarElement
    ? parseFloat(getComputedStyle(sidebarElement).getPropertyValue('--sidebar-collapsed-width')) ||
      64
    : 64

  floatingMenuStyle.value = {
    position: 'fixed',
    left: `${rect.right + 8}px`, // 在菜单项右侧8px处
    top: `${rect.top}px`,
    zIndex: 1000,
    minWidth: '200px',
  }
}

// 检查当前路由是否在子菜单中，如果是则自动展开
const checkAndExpandSubmenu = () => {
  if (props.item.children && props.item.children.length > 0) {
    const hasActiveChild = props.item.children.some((child) => {
      const childPath = resolvePath(child.path)
      return route.path === childPath || route.path.startsWith(childPath)
    })
    if (hasActiveChild) {
      isExpanded.value = true
    }
  }
}

// 初始化时检查是否需要展开
checkAndExpandSubmenu()

// 获取图标组件（简化版，移除冗余的动态加载逻辑）
const getIconComponent = (iconName) => {
  if (!iconName) return null

  // 直接从全局图标注册表获取
  const iconComponent = getIcon(iconName)

  if (!iconComponent) {
    console.warn(`图标 "${iconName}" 未注册，请在 iconRegistry.js 中预注册此图标`)
  }

  return iconComponent
}

// 通用图标获取方法（简化版）
const getMenuIcon = (menuItem) => {
  const iconName = menuItem?.meta?.icon
  if (!iconName) return null

  // 直接从注册表获取
  return getIcon(iconName)
}

// 计算属性：获取当前菜单项的图标
const currentIcon = computed(() => getMenuIcon(props.item))

defineOptions({
  name: 'MenuItem',
})
</script>

<style scoped>
/* ========================================
   MenuItem 组件样式
   使用设计系统中的导航样式
   ======================================== */

/* 菜单项基础样式 */
.modern-menu-item {
  display: block;
  width: 100%;
  padding: 0;
  margin: 2px 8px;
  text-decoration: none;
  border-radius: 6px;
  transition: all 150ms ease;
  position: relative;
  outline: none; /* 移除默认的focus外框 */
}

.modern-menu-item:focus {
  outline: none; /* 确保focus时不显示外框 */
  box-shadow: none; /* 移除可能的阴影 */
}

.modern-menu-item:hover {
  background-color: #EDF2F7;
  text-decoration: none;
}

.modern-menu-item.active {
  background-color: #EBF8FF;
  color: #2B6CB0;
  font-weight: 500;
}

.modern-menu-item.active::before {
  content: "";
  position: absolute;
  left: -8px;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: #2B6CB0;
  border-radius: 0 2px 2px 0;
}

/* 菜单项内容 */
.menu-item-content {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  color: #4A5568;
  transition: color 150ms ease;
  outline: none; /* 移除默认的focus外框 */
}

.menu-item-content:focus {
  outline: none; /* 确保focus时不显示外框 */
  box-shadow: none; /* 移除可能的阴影 */
}

.modern-menu-item:hover .menu-item-content {
  color: #2D3748;
}

.modern-menu-item.active .menu-item-content {
  color: #2B6CB0;
}

/* 菜单图标 */
.menu-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 12px;
  font-size: 18px;
  flex-shrink: 0;
}

/* 菜单标题 */
.menu-title {
  flex: 1;
  font-size: 14px;
  font-weight: 400;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 菜单箭头 */
.menu-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-left: 8px;
  font-size: 12px;
  transition: transform 150ms ease;
  flex-shrink: 0;
}

.menu-arrow.expanded {
  transform: rotate(180deg);
}

/* 收起状态样式 */
.modern-menu-item.collapsed .menu-item-content {
  justify-content: center;
  padding: 12px 8px;
}

.modern-menu-item.collapsed .menu-icon {
  margin-right: 0;
}

/* 子菜单容器 */
.submenu-container {
  overflow: hidden;
  background-color: transparent;
}

.submenu-item-wrapper {
  margin-left: 16px;
}

.submenu-item-wrapper .modern-menu-item {
  margin: 1px 8px;
}

.submenu-item-wrapper .menu-item-content {
  padding-left: 32px;
  font-size: 13px;
}

.submenu-item-wrapper .menu-icon {
  width: 16px;
  height: 16px;
  font-size: 14px;
  margin-right: 8px;
}

/* 悬浮子菜单 */
.floating-submenu {
  position: fixed;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 8px 0;
  min-width: 200px;
  z-index: 1000;
}

.floating-submenu-header {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid #E2E8F0;
  margin-bottom: 4px;
}

.floating-menu-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 12px;
  font-size: 18px;
  color: #2B6CB0;
}

.floating-menu-title {
  font-size: 14px;
  font-weight: 500;
  color: #1A202C;
}

.floating-submenu-content {
  padding: 0;
}

.floating-submenu-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 16px;
  color: #4A5568;
  text-decoration: none;
  transition: all 150ms ease;
  outline: none; /* 移除默认的focus外框 */
}

.floating-submenu-item:focus {
  outline: none; /* 确保focus时不显示外框 */
  box-shadow: none; /* 移除可能的阴影 */
}

.floating-submenu-item:hover {
  background-color: #EDF2F7;
  color: #2B6CB0;
  text-decoration: none;
}

.floating-submenu-item.active {
  background-color: #EBF8FF;
  color: #2B6CB0;
  font-weight: 500;
}

.floating-item-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  flex-shrink: 0;
}

.floating-item-title {
  font-size: 13px;
  line-height: 1.4;
}

/* 动画效果 */
.menu-text-enter-active,
.menu-text-leave-active {
  transition: opacity 200ms ease, transform 200ms ease;
}

.menu-text-enter-from,
.menu-text-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.menu-arrow-enter-active,
.menu-arrow-leave-active {
  transition: opacity 200ms ease, transform 200ms ease;
}

.menu-arrow-enter-from,
.menu-arrow-leave-to {
  opacity: 0;
  transform: translateX(10px);
}

.submenu-enter-active,
.submenu-leave-active {
  transition: all 200ms ease;
  overflow: hidden;
}

.submenu-enter-from,
.submenu-leave-to {
  max-height: 0;
  opacity: 0;
}

.submenu-enter-to,
.submenu-leave-from {
  max-height: 500px;
  opacity: 1;
}

.floating-menu-enter-active,
.floating-menu-leave-active {
  transition: all 150ms ease;
}

.floating-menu-enter-from,
.floating-menu-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}
</style>
