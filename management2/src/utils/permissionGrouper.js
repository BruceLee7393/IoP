/**
 * 权限分组工具
 * 根据后端返回的权限列表，智能推断并构建树形结构
 */

// 权限扩展规则 - 某些权限会自动扩展包含其他权限
const PERMISSION_EXPANSION_RULES = {
  // 暂无扩展规则
}

// 权限分组规则配置
const PERMISSION_GROUP_RULES = {
  // 系统管理模块
  'System': {
    name: '系统管理',
    icon: 'Setting',
    order: 1,
    children: ['UserManagement', 'RoleManagement']
  }
}

// 权限显示名称映射（如果后端 permission_name 不符合预期，使用此映射）
const PERMISSION_DISPLAY_NAMES = {
  'Home': '首页',
  'UserManagement': '用户管理',
  'RoleManagement': '角色管理',
  'OrderManagement': '订单管理'
}

// 权限图标映射
const PERMISSION_ICONS = {
  'Home': 'House',
  'UserManagement': 'User',
  'RoleManagement': 'UserFilled',
  'OrderManagement': 'Document'
}

/**
 * 构建权限树结构
 * @param {Array} permissions - 后端返回的权限列表
 * @param {Object} options - 配置选项
 * @param {boolean} options.includeModuleNodes - 是否包含模块节点（权限配置时为true，导航栏为false）
 * @param {boolean} options.onlyUserPermissions - 是否只显示用户拥有的权限（导航栏为true）
 * @returns {Array} 权限树结构
 */
export function buildPermissionTree(permissions, options = {}) {
  const {
    includeModuleNodes = true,
    onlyUserPermissions = false
  } = options

  // 允许空权限时也构建“首页”
  const inputPermissions = Array.isArray(permissions) ? permissions : []

  // 扩展权限 - 处理点钞管理权限扩展
  let expandedPermissions = [...inputPermissions]
  if (onlyUserPermissions) {
    // 只在构建用户导航菜单时进行权限扩展
    const userPermissionCodes = inputPermissions.map(p => p.permission_code)

    Object.entries(PERMISSION_EXPANSION_RULES).forEach(([mainPermission, expandedPerms]) => {
      if (userPermissionCodes.includes(mainPermission)) {
        expandedPerms.forEach(expandedPerm => {
          if (!userPermissionCodes.includes(expandedPerm)) {
            // 添加虚拟权限（用于导航，但不是真实的后端权限）
            expandedPermissions.push({
              id: `virtual-${expandedPerm}`,
              permission_code: expandedPerm,
              permission_name: PERMISSION_DISPLAY_NAMES[expandedPerm] || expandedPerm
            })
          }
        })
      }
    })

    // 为所有用户添加首页权限
    if (!userPermissionCodes.includes('Home')) {
      expandedPermissions.unshift({
        id: 'virtual-home',
        permission_code: 'Home',
        permission_name: '首页'
      })
    }
  }

  // 创建权限映射表
  const permissionMap = new Map()
  expandedPermissions.forEach(p => {
    permissionMap.set(p.permission_code, p)
  })

  const treeNodes = []
  const processedPermissions = new Set()

  // 优先处理首页权限 - 确保显示在最顶部
  if (onlyUserPermissions && permissionMap.has('Home')) {
    const homePermission = permissionMap.get('Home')
    const homeNode = {
      id: `perm-${homePermission.id}`,
      name: PERMISSION_DISPLAY_NAMES[homePermission.permission_code] || homePermission.permission_name || homePermission.permission_code,
      code: homePermission.permission_code,
      icon: PERMISSION_ICONS[homePermission.permission_code] || 'House',
      type: 'page',
      permissionId: homePermission.id,
      routeName: homePermission.permission_code,
      path: getRoutePathByCode(homePermission.permission_code),
      component: getRouteComponentByCode(homePermission.permission_code),
      meta: {
        title: PERMISSION_DISPLAY_NAMES[homePermission.permission_code] || homePermission.permission_name || homePermission.permission_code,
        icon: PERMISSION_ICONS[homePermission.permission_code] || 'House'
      }
    }
    treeNodes.push(homeNode)
    processedPermissions.add('Home')
  }

  // 处理模块分组
  Object.entries(PERMISSION_GROUP_RULES)
    .sort(([, a], [, b]) => a.order - b.order) // 按顺序排序
    .forEach(([groupKey, groupInfo]) => {
      const children = []

      // 查找该模块下的权限
      groupInfo.children.forEach(childCode => {
        if (permissionMap.has(childCode)) {
          const permission = permissionMap.get(childCode)
                  children.push({
          id: `perm-${permission.id}`,
          name: PERMISSION_DISPLAY_NAMES[childCode] || permission.permission_name || childCode,
          code: childCode,
          icon: PERMISSION_ICONS[childCode] || 'Document',
          type: 'page',
          permissionId: permission.id,
          routeName: childCode, // 对应路由名称
          // 导航栏需要的路径信息
          path: getRoutePathByCode(childCode),
          component: getRouteComponentByCode(childCode),
          meta: {
            title: PERMISSION_DISPLAY_NAMES[childCode] || permission.permission_name || childCode,
            icon: PERMISSION_ICONS[childCode] || 'Document'
          }
        })
          processedPermissions.add(childCode)
        }
      })

      // 如果该模块有权限，创建模块节点
      if (children.length > 0) {
        if (includeModuleNodes) {
          // 权限配置弹窗：包含模块节点
          treeNodes.push({
            id: `module-${groupKey}`,
            name: groupInfo.name,
            code: groupKey,
            icon: groupInfo.icon,
            type: 'module',
            children: children,
            meta: {
              title: groupInfo.name,
              icon: groupInfo.icon
            }
          })
        } else {
          // 导航栏：直接添加子权限，但需要模块信息用于分组显示
          treeNodes.push({
            id: `module-${groupKey}`,
            name: groupInfo.name,
            code: groupKey,
            icon: groupInfo.icon,
            type: 'module',
            path: getModulePathByCode(groupKey),
            children: children,
            meta: {
              title: groupInfo.name,
              icon: groupInfo.icon
            }
          })
        }
      }
    })

  // 处理未分组的独立权限
  expandedPermissions.forEach(permission => {
    if (!processedPermissions.has(permission.permission_code)) {
      const node = {
        id: `perm-${permission.id}`,
        name: PERMISSION_DISPLAY_NAMES[permission.permission_code] || permission.permission_name || permission.permission_code,
        code: permission.permission_code,
        icon: PERMISSION_ICONS[permission.permission_code] || 'Document',
        type: 'page',
        permissionId: permission.id,
        routeName: permission.permission_code,
        path: getRoutePathByCode(permission.permission_code),
        component: getRouteComponentByCode(permission.permission_code),
        meta: {
          title: PERMISSION_DISPLAY_NAMES[permission.permission_code] || permission.permission_name || permission.permission_code,
          icon: PERMISSION_ICONS[permission.permission_code] || 'Document'
        }
      }
      treeNodes.push(node)
    }
  })

  return treeNodes
}

/**
 * 根据权限代码获取路由路径
 */
function getRoutePathByCode(code) {
  const pathMap = {
    'Home': '/home',
    'UserManagement': '/sys_manage/user',
    'RoleManagement': '/sys_manage/role',
    'OrderManagement': '/order'
  }
  return pathMap[code] || `/${code.toLowerCase()}`
}

/**
 * 根据权限代码获取路由组件
 */
function getRouteComponentByCode(code) {
  const componentMap = {
    'Home': () => import('../views/profile/PersonalCenterView.vue'), // 首页显示个人中心内容
    'UserManagement': () => import('../views/sys_manage/UserView.vue'),
    'RoleManagement': () => import('../views/sys_manage/RoleView.vue'),
    'OrderManagement': () => import('../views/order/OrderView.vue')
  }
  return componentMap[code]
}

/**
 * 根据模块代码获取模块路径
 */
function getModulePathByCode(moduleCode) {
  const modulePathMap = {
    'System': '/sys_manage'
  }
  return modulePathMap[moduleCode] || `/${moduleCode.toLowerCase()}`
}

/**
 * 从权限树中提取所有权限ID（用于权限配置）
 */
export function extractPermissionIds(treeNodes) {
  const permissionIds = []

  const traverse = (nodes) => {
    nodes.forEach(node => {
      if (node.permissionId) {
        permissionIds.push(node.permissionId)
      }
      if (node.children) {
        traverse(node.children)
      }
    })
  }

  traverse(treeNodes)
  return permissionIds
}

/**
 * 根据权限ID列表设置树节点的选中状态
 */
export function setTreeCheckedState(treeNodes, checkedPermissionIds) {
  const checkedNodeIds = []

  const traverse = (nodes) => {
    nodes.forEach(node => {
      if (node.permissionId && checkedPermissionIds.includes(node.permissionId)) {
        checkedNodeIds.push(node.id)
      }
      if (node.children) {
        traverse(node.children)
      }
    })
  }

  traverse(treeNodes)
  return checkedNodeIds
}
