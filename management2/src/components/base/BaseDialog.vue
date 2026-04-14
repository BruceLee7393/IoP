<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    :width="width"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :modal="modal"
    :append-to-body="appendToBody"
    :destroy-on-close="destroyOnClose"
    @open="handleOpen"
    @close="handleClose"
    @closed="handleClosed"
  >
    <!-- 对话框内容 -->
    <div class="dialog-content">
      <slot :loading="loading" />
    </div>

    <!-- 对话框底部 -->
    <template #footer>
      <div class="dialog-footer">
        <slot name="footer" :loading="loading" :close="handleClose">
          <!-- 默认按钮 -->
          <el-button @click="handleClose" :disabled="loading">
            {{ cancelText }}
          </el-button>
          <el-button 
            v-if="showConfirm"
            type="primary" 
            @click="handleConfirm" 
            :loading="loading"
          >
            {{ confirmText }}
          </el-button>
        </slot>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, watch, nextTick } from 'vue'

// Props定义
const props = defineProps({
  // 对话框显示状态
  modelValue: {
    type: Boolean,
    required: true,
  },
  // 对话框标题
  title: {
    type: String,
    default: '对话框',
  },
  // 对话框宽度
  width: {
    type: [String, Number],
    default: '50%',
  },
  // 加载状态
  loading: {
    type: Boolean,
    default: false,
  },
  // 按钮文本
  confirmText: {
    type: String,
    default: '确定',
  },
  cancelText: {
    type: String,
    default: '取消',
  },
  // 是否显示确认按钮
  showConfirm: {
    type: Boolean,
    default: true,
  },
  // Element Plus Dialog 原生属性
  closeOnClickModal: {
    type: Boolean,
    default: false,
  },
  closeOnPressEscape: {
    type: Boolean,
    default: true,
  },
  showClose: {
    type: Boolean,
    default: true,
  },
  modal: {
    type: Boolean,
    default: true,
  },
  appendToBody: {
    type: Boolean,
    default: false,
  },
  destroyOnClose: {
    type: Boolean,
    default: false,
  },
})

// Emits定义
const emit = defineEmits([
  'update:modelValue',
  'confirm',
  'cancel',
  'open',
  'close',
  'closed'
])

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 事件处理
const handleOpen = () => {
  emit('open')
}

const handleClose = () => {
  emit('cancel')
  emit('update:modelValue', false)
}

const handleClosed = () => {
  emit('closed')
}

const handleConfirm = () => {
  emit('confirm')
}

// 监听对话框打开状态
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    nextTick(() => {
      // 对话框打开后的处理逻辑
    })
  }
})

// 暴露方法给父组件
defineExpose({
  close: handleClose,
})
</script>

<style scoped>
.dialog-content {
  min-height: 100px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 90% !important;
    margin: 5vh auto;
  }
  
  .dialog-footer {
    flex-direction: column-reverse;
    gap: 8px;
  }
  
  .dialog-footer .el-button {
    width: 100%;
  }
}

/* 对话框样式优化 */
:deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 24px;
  margin: 0;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
  font-size: 18px;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px 24px;
  background-color: #f8f9fa;
}
</style>
