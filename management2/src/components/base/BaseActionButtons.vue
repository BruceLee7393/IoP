<template>
  <div class="action-buttons" :class="{ 'action-buttons--vertical': vertical }">
    <template v-for="action in visibleActions" :key="action.key">
      <!-- 普通按钮 -->
      <el-button
        v-if="action.type !== 'dropdown'"
        :type="action.buttonType || action.type || 'primary'"
        :size="action.size || size"
        :disabled="action.disabled"
        :loading="action.loading"
        :plain="action.plain"
        :round="action.round"
        :circle="action.circle"
        :class="action.class || getActionClass(action)"
        @click="handleAction(action)"
      >
        <el-icon v-if="action.icon" class="button-icon">
          <component :is="getIconComponent(action.icon)" />
        </el-icon>
        {{ action.label }}
      </el-button>

      <!-- 下拉按钮 -->
      <el-dropdown
        v-else
        :size="action.size || size"
        :disabled="action.disabled"
        @command="(command) => handleDropdownAction(action, command)"
      >
        <el-button
          :type="action.buttonType || action.type || 'primary'"
          :size="action.size || size"
          :disabled="action.disabled"
          :class="action.class || getActionClass(action)"
        >
          <el-icon v-if="action.icon" class="button-icon">
            <component :is="getIconComponent(action.icon)" />
          </el-icon>
          {{ action.label }}
          <el-icon class="el-icon--right">
            <ArrowDown />
          </el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-for="item in action.items"
              :key="item.key"
              :command="item.key"
              :disabled="item.disabled"
              :divided="item.divided"
            >
              <el-icon v-if="item.icon" class="dropdown-icon">
                <component :is="item.icon" />
              </el-icon>
              {{ item.label }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  ArrowDown,
  Plus,
  Delete,
  Download,
  Edit,
  View,
  Search,
  Refresh,
} from '@element-plus/icons-vue'

// Props定义
const props = defineProps({
  // 操作按钮配置数组
  actions: {
    type: Array,
    required: true,
    default: () => [],
  },
  // 按钮尺寸
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['large', 'default', 'small'].includes(value),
  },
  // 垂直布局
  vertical: {
    type: Boolean,
    default: false,
  },
  // 权限检查函数
  permissionCheck: {
    type: Function,
    default: null,
  },
  // 上下文数据（用于条件显示）
  context: {
    type: Object,
    default: () => ({}),
  },
})

// Emits定义
const emit = defineEmits(['action'])

// 计算属性
const visibleActions = computed(() => {
  return props.actions.filter((action) => {
    // 权限检查
    if (action.permission && props.permissionCheck) {
      if (!props.permissionCheck(action.permission)) {
        return false
      }
    }

    // 条件显示检查
    if (action.show && typeof action.show === 'function') {
      return action.show(props.context)
    }

    // 默认显示
    return action.show !== false
  })
})

// 图标映射
const iconMap = {
  Plus,
  Delete,
  Download,
  Edit,
  View,
  Search,
  Refresh,
  ArrowDown,
}

// 获取图标组件
const getIconComponent = (iconName) => {
  if (typeof iconName === 'string') {
    return iconMap[iconName] || iconName
  }
  return iconName
}

// 事件处理
const handleAction = (action) => {
  if (action.disabled) return

  emit('action', {
    key: action.key,
    action: action.action || action.key,
    data: action.data,
    context: props.context,
  })
}

const handleDropdownAction = (parentAction, command) => {
  const item = parentAction.items.find((item) => item.key === command)
  if (!item || item.disabled) return

  emit('action', {
    key: command,
    action: item.action || command,
    data: item.data,
    context: props.context,
    parent: parentAction.key,
  })
}

// 获取操作按钮的CSS类
const getActionClass = (action) => {
  const keyClassMap = {
    create: 'btn-add',
    add: 'btn-add',
    export: 'btn-export',
    upload: 'btn-upload',
    search: 'btn-search',
    reset: 'btn-reset',
    edit: 'btn-edit',
    delete: 'btn-delete',
    view: 'btn-view',
    download: 'btn-download',
    toggle: 'btn-toggle',
  }
  return keyClassMap[action.key] || keyClassMap[action.action] || ''
}
</script>

<style scoped>
.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.action-buttons--vertical {
  flex-direction: column;
  align-items: stretch;
}

.action-buttons--vertical .el-button {
  width: 100%;
  justify-content: flex-start;
}

.dropdown-icon {
  margin-right: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
    gap: 8px;
  }

  .action-buttons .el-button {
    width: 100%;
    justify-content: center;
  }
}

/* 按钮组样式优化 */
.action-buttons .el-button + .el-button {
  margin-left: 0;
}

.action-buttons .el-dropdown + .el-button,
.action-buttons .el-button + .el-dropdown {
  margin-left: 0;
}
</style>
