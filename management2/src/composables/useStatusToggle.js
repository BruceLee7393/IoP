// src/composables/useStatusToggle.js
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

/**
 * 状态切换通用逻辑（启用/禁用、上线/下线等）
 * @param {Object} api - API模块对象
 * @param {Object} options - 配置选项
 */
export function useStatusToggle(api, options = {}) {
  const {
    statusField = 'isEnabled',
    entityName = '记录',
    statusLabels = {
      true: '启用',
      false: '禁用',
    },
    confirmMessages = {
      true: (name) => `确定要启用${entityName} [${name}] 吗？`,
      false: (name) => `确定要禁用${entityName} [${name}] 吗？`,
    },
    successMessages = {
      true: '启用成功',
      false: '禁用成功',
    },
    errorMessages = {
      true: '启用失败，请稍后重试',
      false: '禁用失败，请稍后重试',
    },
    onSuccess = () => {},
    onError = () => {},
  } = options

  // 响应式状态
  const loading = ref(false)
  const toggleLoading = ref({}) // 用于跟踪单个记录的切换状态

  /**
   * 切换单个记录的状态
   * @param {Object} record - 记录对象
   * @param {Function} afterToggle - 切换后的回调函数
   * @param {Object} customOptions - 自定义选项
   */
  const toggleStatus = async (record, afterToggle = null, customOptions = {}) => {
    const {
      field = statusField,
      labels = statusLabels,
      confirmMsg = confirmMessages,
      successMsg = successMessages,
      errorMsg = errorMessages,
    } = customOptions

    const currentStatus = record[field]
    const newStatus = !currentStatus
    const actionText = labels[newStatus] || (newStatus ? '启用' : '禁用')
    const recordName = record.name || record.title || record.id || entityName

    try {
      // 显示确认对话框
      const confirmMessage =
        typeof confirmMsg[newStatus] === 'function'
          ? confirmMsg[newStatus](recordName)
          : confirmMsg[newStatus] || `确定要${actionText}${entityName} [${recordName}] 吗？`

      await ElMessageBox.confirm(confirmMessage, '提示', {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      })

      // 设置加载状态
      toggleLoading.value[record.id] = true

      // 调用API
      let result
      if (api.setStatus) {
        result = await api.setStatus(record.id, newStatus)
      } else if (api.toggleStatus) {
        result = await api.toggleStatus(record.id, field, newStatus)
      } else if (api.update) {
        result = await api.update({ ...record, [field]: newStatus })
      } else {
        throw new Error('No suitable API method found for status toggle')
      }

      // 更新本地状态
      record[field] = newStatus

      // 显示成功消息
      const successMessage = successMsg[newStatus] || `${actionText}成功`
      ElMessage.success(successMessage)

      // 执行回调
      onSuccess(record, newStatus, field)
      if (afterToggle) {
        afterToggle(record, newStatus, field)
      }

      return result
    } catch (error) {
      if (error !== 'cancel') {
        const errorMessage = errorMsg[newStatus] || `${actionText}失败，请稍后重试`
        ElMessage.error(errorMessage)
        onError(error, record, newStatus, field)
      }
      throw error
    } finally {
      toggleLoading.value[record.id] = false
    }
  }

  /**
   * 批量切换状态
   * @param {Array} records - 记录数组
   * @param {boolean} targetStatus - 目标状态
   * @param {Function} afterBatchToggle - 批量切换后的回调函数
   * @param {Object} customOptions - 自定义选项
   */
  const batchToggleStatus = async (
    records,
    targetStatus,
    afterBatchToggle = null,
    customOptions = {},
  ) => {
    const {
      field = statusField,
      labels = statusLabels,
      successMsg = successMessages,
      errorMsg = errorMessages,
    } = customOptions

    if (!records || records.length === 0) {
      ElMessage.warning('请选择要操作的记录')
      return
    }

    const actionText = labels[targetStatus] || (targetStatus ? '启用' : '禁用')

    try {
      await ElMessageBox.confirm(
        `确定要${actionText}选中的 ${records.length} 个${entityName}吗？`,
        '批量操作确认',
        {
          type: 'warning',
          confirmButtonText: '确定',
          cancelButtonText: '取消',
        },
      )

      loading.value = true

      // 批量处理
      const promises = records.map(async (record) => {
        try {
          if (api.setStatus) {
            await api.setStatus(record.id, targetStatus)
          } else if (api.toggleStatus) {
            await api.toggleStatus(record.id, field, targetStatus)
          } else if (api.update) {
            await api.update({ ...record, [field]: targetStatus })
          }

          // 更新本地状态
          record[field] = targetStatus
          return { success: true, record }
        } catch (error) {
          return { success: false, record, error }
        }
      })

      const results = await Promise.all(promises)
      const successCount = results.filter((r) => r.success).length
      const failCount = results.length - successCount

      // 显示结果消息
      if (failCount === 0) {
        ElMessage.success(`成功${actionText} ${successCount} 个${entityName}`)
      } else if (successCount === 0) {
        ElMessage.error(`${actionText}失败，请稍后重试`)
      } else {
        ElMessage.warning(`${actionText}完成：成功 ${successCount} 个，失败 ${failCount} 个`)
      }

      // 执行回调
      onSuccess(records, targetStatus, field, results)
      if (afterBatchToggle) {
        afterBatchToggle(records, targetStatus, field, results)
      }

      return results
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error(`批量${actionText}失败，请稍后重试`)
        onError(error, records, targetStatus, field)
      }
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取状态显示文本
   * @param {any} status - 状态值
   * @param {Object} customLabels - 自定义标签
   */
  const getStatusText = (status, customLabels = statusLabels) => {
    return customLabels[status] || status
  }

  /**
   * 获取状态类型（用于el-tag等组件）
   * @param {any} status - 状态值
   * @param {Object} typeMap - 类型映射
   */
  const getStatusType = (status, typeMap = { true: 'success', false: 'danger' }) => {
    return typeMap[status] || 'info'
  }

  /**
   * 检查记录是否正在切换状态
   * @param {string|number} recordId - 记录ID
   */
  const isToggling = (recordId) => {
    return toggleLoading.value[recordId] || false
  }

  /**
   * 清除所有切换状态
   */
  const clearToggleStates = () => {
    toggleLoading.value = {}
  }

  return {
    // 状态
    loading,
    toggleLoading,

    // 方法
    toggleStatus,
    batchToggleStatus,
    getStatusText,
    getStatusType,
    isToggling,
    clearToggleStates,
  }
}
