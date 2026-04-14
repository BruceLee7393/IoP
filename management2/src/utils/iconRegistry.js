// 全局图标注册系统
import {
  DataLine,
  Setting,
  Cpu,
  Upload,
  Document,
  Tickets,
  Money,
  User,
  UserFilled,
  Files,
  OfficeBuilding,
  ArrowDown,
  Search,
  List,
  Warning,
  Tools,
  Monitor,
  Timer,
  House,
  // 可以继续添加更多图标
} from '@element-plus/icons-vue'

// 图标注册表
const iconRegistry = new Map()

// 预注册常用图标
const preRegisteredIcons = {
  DataLine,
  Setting,
  Cpu,
  Upload,
  Document,
  Tickets,
  Money,
  User,
  UserFilled,
  Files,
  OfficeBuilding,
  ArrowDown,
  Search,
  List,
  Warning,
  Tools,
  Monitor,
  Timer,
  House,
}

// 批量注册预定义图标
Object.entries(preRegisteredIcons).forEach(([name, component]) => {
  iconRegistry.set(name, component)
})

/**
 * 注册单个图标
 * @param {string} name - 图标名称
 * @param {Component} component - 图标组件
 */
export const registerIcon = (name, component) => {
  iconRegistry.set(name, component)
}

/**
 * 批量注册图标
 * @param {Object} icons - 图标对象 { name: component }
 */
export const registerIcons = (icons) => {
  Object.entries(icons).forEach(([name, component]) => {
    iconRegistry.set(name, component)
  })
}

/**
 * 获取图标组件
 * @param {string} name - 图标名称
 * @returns {Component|null} 图标组件或null
 */
export const getIcon = (name) => {
  return iconRegistry.get(name) || null
}

/**
 * 检查图标是否存在
 * @param {string} name - 图标名称
 * @returns {boolean} 是否存在
 */
export const hasIcon = (name) => {
  return iconRegistry.has(name)
}

/**
 * 获取所有已注册的图标名称
 * @returns {string[]} 图标名称数组
 */
export const getRegisteredIconNames = () => {
  return Array.from(iconRegistry.keys())
}

// 导出图标注册表（只读）
export const icons = new Proxy(iconRegistry, {
  get(target, prop) {
    return target.get(prop)
  },
  set() {
    console.warn('Use registerIcon() or registerIcons() to add icons')
    return false
  },
  deleteProperty() {
    console.warn('Icons cannot be deleted from registry')
    return false
  },
})

export default {
  registerIcon,
  registerIcons,
  getIcon,
  hasIcon,
  getRegisteredIconNames,
  icons,
}
