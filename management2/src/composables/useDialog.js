import { ref, computed } from 'vue'

/**
 * 通用Dialog状态管理
 * @param {Object} options 配置选项
 * @returns {Object} Dialog状态和控制方法
 */
export function useDialog(options = {}) {
  const { defaultVisible = false, onOpen = null, onClose = null, onClosed = null } = options

  // 状态管理
  const visible = ref(defaultVisible)
  const loading = ref(false)
  const data = ref(null)

  // 计算属性
  const isOpen = computed(() => visible.value)

  // 打开对话框
  const open = (payload = null) => {
    if (payload !== null) {
      data.value = payload
    }
    visible.value = true
    onOpen?.(payload)
  }

  // 关闭对话框
  const close = () => {
    visible.value = false
    onClose?.()
  }

  // 对话框完全关闭后的处理
  const handleClosed = () => {
    // 清理数据
    data.value = null
    loading.value = false
    onClosed?.()
  }

  // 设置加载状态
  const setLoading = (state) => {
    loading.value = state
  }

  // 设置数据
  const setData = (newData) => {
    data.value = newData
  }

  // 切换显示状态
  const toggle = () => {
    if (visible.value) {
      close()
    } else {
      open()
    }
  }

  return {
    // 状态
    visible,
    loading,
    data,
    isOpen,

    // 方法
    open,
    close,
    toggle,
    setLoading,
    setData,
    handleClosed,
  }
}

/**
 * 表单Dialog状态管理
 * @param {Object} options 配置选项
 * @returns {Object} 表单Dialog状态和控制方法
 */
export function useFormDialog(options = {}) {
  const {
    initialData = {},
    onSubmit = null,
    onSuccess = null,
    onError = null,
    resetOnClose = true,
    ...dialogOptions
  } = options

  const dialog = useDialog(dialogOptions)
  const isEdit = ref(false)
  const formData = ref({ ...initialData })
  const originalData = ref({ ...initialData })

  // 打开新增表单
  const openAdd = (defaultData = {}) => {
    isEdit.value = false
    formData.value = { ...initialData, ...defaultData }
    originalData.value = { ...formData.value }
    dialog.open()
  }

  // 打开编辑表单
  const openEdit = (editData) => {
    isEdit.value = true
    formData.value = { ...editData }
    originalData.value = { ...editData }
    dialog.open(editData)
  }

  // 重置表单
  const resetForm = () => {
    formData.value = { ...originalData.value }
  }

  // 提交表单
  const handleSubmit = async () => {
    if (!onSubmit) return

    dialog.setLoading(true)
    try {
      const result = await onSubmit(formData.value, isEdit.value)
      onSuccess?.(result, formData.value, isEdit.value)
      if (resetOnClose) {
        dialog.close()
      }
      return result
    } catch (error) {
      onError?.(error, formData.value, isEdit.value)
      throw error
    } finally {
      dialog.setLoading(false)
    }
  }

  // 关闭时重置
  const handleClose = () => {
    if (resetOnClose) {
      formData.value = { ...initialData }
    }
    dialog.close()
  }

  return {
    ...dialog,

    // 表单特有状态
    isEdit,
    formData,
    originalData,

    // 表单特有方法
    openAdd,
    openEdit,
    resetForm,
    handleSubmit,
    handleClose,

    // 重写关闭方法
    close: handleClose,
  }
}

/**
 * 确认Dialog状态管理
 * @param {Object} options 配置选项
 * @returns {Object} 确认Dialog状态和控制方法
 */
export function useConfirmDialog(options = {}) {
  const { onConfirm = null, onCancel = null, confirmAsync = false, ...dialogOptions } = options

  const dialog = useDialog(dialogOptions)

  // 确认操作
  const handleConfirm = async () => {
    if (!onConfirm) {
      dialog.close()
      return
    }

    if (confirmAsync) {
      dialog.setLoading(true)
      try {
        await onConfirm(dialog.data.value)
        dialog.close()
      } catch (error) {
        // 错误处理由调用方决定
        throw error
      } finally {
        dialog.setLoading(false)
      }
    } else {
      onConfirm(dialog.data.value)
      dialog.close()
    }
  }

  // 取消操作
  const handleCancel = () => {
    onCancel?.(dialog.data.value)
    dialog.close()
  }

  // 打开确认对话框
  const confirm = (data, options = {}) => {
    dialog.setData({ ...data, ...options })
    dialog.open()
  }

  return {
    ...dialog,

    // 确认Dialog特有方法
    confirm,
    handleConfirm,
    handleCancel,
  }
}

/**
 * 查看Dialog状态管理
 * @param {Object} options 配置选项
 * @returns {Object} 查看Dialog状态和控制方法
 */
export function useViewDialog(options = {}) {
  const { loadData = null, loadOnOpen = true, ...dialogOptions } = options

  const dialog = useDialog(dialogOptions)

  // 加载数据
  const loadViewData = async (id) => {
    if (!loadData) return

    dialog.setLoading(true)
    try {
      const data = await loadData(id)
      dialog.setData(data)
      return data
    } finally {
      dialog.setLoading(false)
    }
  }

  // 打开查看对话框
  const openView = async (idOrData) => {
    dialog.open()

    if (loadOnOpen && loadData) {
      // 如果是ID，则加载数据
      if (typeof idOrData === 'string' || typeof idOrData === 'number') {
        await loadViewData(idOrData)
      } else {
        // 如果是数据对象，直接设置
        dialog.setData(idOrData)
      }
    } else {
      // 直接设置数据
      dialog.setData(idOrData)
    }
  }

  return {
    ...dialog,

    // 查看Dialog特有方法
    openView,
    loadViewData,
  }
}
