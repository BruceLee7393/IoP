// src/composables/useCrud.js
import { ref, reactive, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useDeleteConfirmation } from './useDeleteConfirmation'
 
// 错误提示节流，避免重复显示相同错误
const ERROR_THROTTLE_MS = 3000
const errorTimestamps = new Map()
const shouldShowError = (message, throttleMs = ERROR_THROTTLE_MS) => {
  const now = Date.now()
  const last = errorTimestamps.get(message) || 0
  if (now - last > throttleMs) {
    errorTimestamps.set(message, now)
    return true
  }
  return false
}

/**
 * CRUD操作通用逻辑
 * @param {Object} api - API模块对象，包含 add, update, del 等方法
 * @param {Object} options - 配置选项
 */
export function useCrud(api, options = {}) {
  const {
    entityName = '记录',
    successMessages = {
      add: '添加成功',
      update: '修改成功',
      delete: '删除成功',
    },
    errorMessages = {
      add: '添加失败，请稍后重试',
      update: '修改失败，请稍后重试',
      delete: '删除失败，请稍后重试',
    },
    onSuccess = () => {},
    onError = () => {},
  } = options

  // 响应式状态
  const loading = ref(false)
  const submitLoading = ref(false)

  // 对话框状态
  const dialog = reactive({
    visible: false,
    title: '',
    isEdit: false,
    data: null, // 初始化data属性
  })

  // 删除确认逻辑
  const { showDeleteConfirmation } = useDeleteConfirmation()

  /**
   * 提交表单（添加/修改）
   * @param {Object} formData - 表单数据
   */
  const submitForm = async (formData) => {
    console.log('useCrud submitForm called:', {
      isEdit: dialog.isEdit,
      formData,
      dialogData: dialog.data,
    })
    try {
      submitLoading.value = true
      if (dialog.isEdit) {
        // 修改操作 - 清理数据，只移除undefined字段
        const cleanData = {}
        Object.keys(formData).forEach((key) => {
          const value = formData[key]
          // 保留所有字段，只跳过undefined
          // 将null值转换为空字符串，避免后端验证失败
          if (value !== undefined) {
            cleanData[key] = value === null ? '' : value
          }
        })
        delete cleanData.id
        delete cleanData.account

        // 如果是编辑模式且密码为空，则不发送密码字段
        if (dialog.isEdit && (!cleanData.password || cleanData.password === '')) {
          delete cleanData.password
        }

        console.log('useCrud calling api.update with cleaned data:', cleanData)
        await api.update(dialog.data.id, cleanData)
        ElMessage.success(successMessages.update || '修改成功')
      } else {
        // 添加操作
        console.log('useCrud calling api.create with:', formData)
        await api.create(formData)
        ElMessage.success(successMessages.add || '添加成功')
      }
      dialog.visible = false
      console.log('useCrud calling onSuccess callback')
      onSuccess()
      // 通知全局：实体数据已变更，用于刷新下拉选项等缓存
      try {
        window.dispatchEvent(
          new CustomEvent('entity-changed', {
            detail: { entityName, action: dialog.isEdit ? 'update' : 'add' },
          }),
        )
      } catch (e) {}
    } catch (error) {
      console.error('useCrud submitForm error:', error)

      // 优先使用后端返回的错误信息，避免重复显示
      let errorMessage = null

      // 检查是否是HTTP错误响应
      if (error.response && error.response.data) {
        const responseData = error.response.data
        // 优先使用后端返回的message
        errorMessage = responseData.message || responseData.msg || responseData.error
      }

      // 如果没有后端错误信息，使用默认消息
      if (!errorMessage) {
        errorMessage = dialog.isEdit ? errorMessages.update : errorMessages.add
      }

      // 显示错误消息，使用节流避免重复显示
      const finalMessage = errorMessage || '操作失败'
      if (shouldShowError(finalMessage)) {
        ElMessage.error(finalMessage)
      }
    } finally {
      submitLoading.value = false
    }
  }

  /**
   * 打开添加对话框
   * @param {Object} defaultData - 默认数据
   */
  const openAddDialog = (defaultData = {}) => {
    dialog.data = { ...defaultData } // 赋值给dialog.data
    dialog.isEdit = false
    dialog.title = `添加${entityName}`
    dialog.visible = true
  }

  /**
   * 打开编辑对话框
   * @param {Object} data - 编辑的数据
   */
  const openEditDialog = (data) => {
    if (!data) return
    dialog.data = { ...data } // 赋值给dialog.data
    dialog.isEdit = true
    dialog.title = `修改${entityName}`
    dialog.visible = true
  }

  /**
   * 关闭对话框
   */
  const closeDialog = () => {
    dialog.visible = false
  }

  /**
   * 删除单个记录
   * @param {Object} row - 要删除的记录
   * @param {Function} afterDelete - 删除后的处理函数
   */
  const deleteRecord = async (row, afterDelete) => {
    // 优先使用有意义的名称字段，对于设备使用device_id
    let itemName
    if (row.device_id) {
      // 设备显示：设备ID (型号名称)
      itemName = row.model_name ? `${row.device_id} (${row.model_name})` : row.device_id
    } else if (row.order_number && row.model) {
      // 订单显示：订单号 (机型)
      itemName = `${row.order_number} (${row.model})`
    } else {
      // 其他实体使用原有逻辑
      itemName =
        row.full_name ||
        row.role_name ||
      
        row.name ||
        row.title ||
        row.account ||
        row.model_name ||
        `${entityName}(${row.id})`
    }

    try {
      await showDeleteConfirmation({
        title: `删除${entityName}确认`,
        message: `确定要删除${entityName} [${itemName}] 吗？删除后无法恢复！`,
        countdown: 3,
      })

      const result = await api.delete(row.id)
      // 检查API返回结果
      if (result === false) {
        throw new Error('删除操作失败')
      }

      ElMessage.success(successMessages.delete)
      onSuccess('delete', row)
      // 广播删除事件
      try {
        window.dispatchEvent(
          new CustomEvent('entity-changed', { detail: { entityName, action: 'delete' } }),
        )
      } catch (e) {}
      if (afterDelete) {
        afterDelete(row)
      }
    } catch (error) {
      console.error('删除操作错误:', error)
      if (error === 'cancel' || error === 'close') {
        // 用户取消删除，显示取消提示
        ElMessage.info('已取消删除操作')
      } else {
        // 实际删除失败
        const errorMsg = error.message || errorMessages.delete
        ElMessage.error(errorMsg)
        onError('delete', error)
      }
    }
  }

  /**
   * 批量删除记录
   * @param {Array} ids - 要删除的ID数组
   * @param {Function} afterDelete - 删除后的处理函数
   */
  const batchDelete = async (ids, afterDelete) => {
    if (!ids || ids.length === 0) {
      ElMessage.warning('请选择要删除的记录')
      return
    }

    try {
      await showDeleteConfirmation({
        title: `批量删除${entityName}确认`,
        message: `确定要删除选中的 ${ids.length} 个${entityName}吗？删除后无法恢复！`,
        countdown: 3,
      })

      // 批量删除
      let result
      if (api.batchDelete) {
        result = await api.batchDelete(ids)
      } else {
        const results = await Promise.all(ids.map((id) => api.delete(id)))
        result = results.every((r) => r !== false)
      }

      // 检查批量删除结果
      if (result === false) {
        throw new Error('批量删除操作失败')
      }

      ElMessage.success(`成功删除 ${ids.length} 个${entityName}`)
      onSuccess('batchDelete', ids)
      if (afterDelete) {
        afterDelete(ids)
      }
    } catch (error) {
      console.error('批量删除操作错误:', error)
      if (error === 'cancel') {
        // 用户取消删除，显示取消提示
        ElMessage.info('已取消批量删除操作')
      } else {
        // 实际删除失败
        const errorMsg = error.message || errorMessages.delete
        ElMessage.error(errorMsg)
        onError('batchDelete', error)
      }
    }
  }

  /**
   * 切换状态（启用/禁用）
   * @param {Object} row - 记录对象
   * @param {string} statusField - 状态字段名
   * @param {Function} afterToggle - 切换后的处理函数
   */
  const toggleStatus = async (row, statusField = 'status', afterToggle) => {
    // 对于用户状态，active/disabled 切换
    const currentStatus = row[statusField]
    const newStatus = currentStatus === 'active' ? 'disabled' : 'active'
    const actionText = newStatus === 'active' ? '启用' : '禁用'

    try {
      await ElMessageBox.confirm(
        `确定要${actionText}${entityName} [${row.full_name || row.name || row.id}] 吗？`,
        '状态变更确认',
        { type: 'warning' },
      )

      // 调用状态切换API
      if (api.updateStatus) {
        await api.updateStatus(row.id, newStatus)
      } else if (api.setStatus) {
        await api.setStatus(row.id, newStatus)
      } else {
        // 如果没有专门的状态切换API，使用update
        await api.update(row.id, { [statusField]: newStatus })
      }

      row[statusField] = newStatus
      ElMessage.success(`${actionText}成功`)

      onSuccess('toggleStatus', { row, statusField, newStatus })
      // 广播状态变更
      try {
        window.dispatchEvent(
          new CustomEvent('entity-changed', { detail: { entityName, action: 'toggleStatus' } }),
        )
      } catch (e) {}
      if (afterToggle) {
        afterToggle(row, newStatus)
      }
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error(`${actionText}失败，请稍后重试`)
        onError('toggleStatus', error)
      }
    }
  }

  return {
    // 状态
    loading,
    submitLoading,

    // 对话框状态
    dialog,

    // 方法
    openAddDialog,
    openEditDialog,
    deleteRecord,
    batchDelete,
    toggleStatus,
    submitForm,
  }
}
