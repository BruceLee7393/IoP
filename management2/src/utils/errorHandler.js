// src/utils/errorHandler.js
import { ElMessage, ElNotification } from 'element-plus'

// 统一的错误提示节流，避免同一时段多处同时报错导致刷屏
const ERROR_THROTTLE_MS = 4000
const errorDisplayTimestamps = new Map()
const shouldDisplayError = (key, throttleMs = ERROR_THROTTLE_MS) => {
  const now = Date.now()
  const last = errorDisplayTimestamps.get(key) || 0
  if (now - last > throttleMs) {
    errorDisplayTimestamps.set(key, now)
    return true
  }
  return false
}

/**
 * 字段名称映射表 - 将英文字段名转换为中文
 */
const FIELD_NAME_MAP = {
  // 用户相关字段
  username: '用户名',
  password: '密码',
  email: '邮箱',
  phone: '手机号',
  real_name: '真实姓名',
  role_id: '角色',
  status: '状态',

  // 设备相关字段
  device_id: '设备ID',
  model_id: '设备型号',
  institution_id: '机构',
  ip_endpoint: 'IP地址',
  firmware_version: '固件版本',
  description: '描述',

  // 机构相关字段
  institution_name: '机构名称',
  institution_code: '机构编码',
  parent_id: '上级机构',

  // 角色相关字段
  role_name: '角色名称',
  role_code: '角色编码',
  permissions: '权限',

  // 订单相关字段
  order_number: '订单号',
  model: '机型',
  part_number: '料号',
  serial_number_start: '起始序列号',
  serial_number_end: '结束序列号',
  order_created_at: '生产日期',
  component_part_number: '组件料号',
  sub_component_part_number: '子组件料号',

  // 通用字段
  name: '名称',
  code: '编码',
  title: '标题',
  content: '内容',
  remark: '备注',
  sort_order: '排序',
  created_at: '创建时间',
  updated_at: '更新时间',
}

/**
 * 错误消息映射表 - 将英文错误消息转换为中文
 */
const ERROR_MESSAGE_MAP = {
  // 长度验证
  'Shorter than minimum length': '长度不能少于',
  'Longer than maximum length': '长度不能超过',
  'Length must be': '长度必须为',
  

  // 必填验证
  'Missing data for required field': '不能为空',
  'Field may not be null': '不能为空',
  'This field is required': '不能为空',

  // 格式验证
  'Not a valid email address': '邮箱格式不正确',
  'Not a valid phone number': '手机号格式不正确',
  'Not a valid URL': '网址格式不正确',
  'Not a valid integer': '必须是整数',
  'Not a valid number': '必须是数字',
  'Not a valid datetime': '日期时间格式不正确',

  // 唯一性验证
  'Already exists': '已存在',
  'Duplicate entry': '重复的条目',
  'Must be unique': '必须唯一',

  // 范围验证
  'Must be greater than': '必须大于',
  'Must be less than': '必须小于',
  'Must be between': '必须在范围内',

  // 选择验证
  'Not a valid choice': '选择无效',
  'Invalid option': '选项无效',

  // 未知字段
  'Unknown field': '未知字段',

}

/**
 * 解析422验证错误
 * @param {Object} errorData - 后端返回的错误数据
 * @returns {Array} 解析后的错误信息数组
 */
export function parse422ValidationErrors(errorData) {
  const errors = []

  try {
    // 检查是否有errors.json结构
    const validationErrors = errorData?.errors?.json || errorData?.errors || {}

    Object.keys(validationErrors).forEach((fieldName) => {
      const fieldErrors = validationErrors[fieldName]
      const fieldDisplayName = FIELD_NAME_MAP[fieldName] || fieldName

      if (Array.isArray(fieldErrors)) {
        fieldErrors.forEach((errorMsg) => {
          const friendlyMessage = translateErrorMessage(errorMsg, fieldDisplayName)
          errors.push({
            field: fieldName,
            fieldDisplayName,
            originalMessage: errorMsg,
            friendlyMessage,
          })
        })
      } else if (typeof fieldErrors === 'string') {
        const friendlyMessage = translateErrorMessage(fieldErrors, fieldDisplayName)
        errors.push({
          field: fieldName,
          fieldDisplayName,
          originalMessage: fieldErrors,
          friendlyMessage,
        })
      }
    })
  } catch (error) {
    console.error('解析422错误失败:', error)
  }

  return errors
}

/**
 * 将英文错误消息转换为中文友好提示
 * @param {string} originalMessage - 原始英文错误消息
 * @param {string} fieldDisplayName - 字段中文名称
 * @returns {string} 友好的中文错误消息
 */
function translateErrorMessage(originalMessage, fieldDisplayName) {
  // 处理长度验证错误
  const lengthMatch = originalMessage.match(/Shorter than minimum length (\d+)/)
  if (lengthMatch) {
    return `${fieldDisplayName}长度不能少于${lengthMatch[1]}个字符`
  }

  const maxLengthMatch = originalMessage.match(/Longer than maximum length (\d+)/)
  if (maxLengthMatch) {
    return `${fieldDisplayName}长度不能超过${maxLengthMatch[1]}个字符`
  }

  const exactLengthMatch = originalMessage.match(/Length must be (\d+)/)
  if (exactLengthMatch) {
    return `${fieldDisplayName}长度必须为${exactLengthMatch[1]}个字符`
  }

  // 处理范围验证错误
  const greaterThanMatch = originalMessage.match(/Must be greater than (\d+)/)
  if (greaterThanMatch) {
    return `${fieldDisplayName}必须大于${greaterThanMatch[1]}`
  }

  const lessThanMatch = originalMessage.match(/Must be less than (\d+)/)
  if (lessThanMatch) {
    return `${fieldDisplayName}必须小于${lessThanMatch[1]}`
  }

  // 处理其他常见错误
  for (const [englishMsg, chineseMsg] of Object.entries(ERROR_MESSAGE_MAP)) {
    if (originalMessage.includes(englishMsg)) {
      if (chineseMsg === '不能为空') {
        return `${fieldDisplayName}${chineseMsg}`
      } else if (chineseMsg.includes('格式不正确')) {
        return `${fieldDisplayName}${chineseMsg}`
      } else {
        return `${fieldDisplayName}${chineseMsg}`
      }
    }
  }

  // 如果没有匹配的翻译，返回原始消息
  return `${fieldDisplayName}: ${originalMessage}`
}

/**
 * 显示友好的验证错误提示
 * @param {Array} errors - 解析后的错误信息数组
 * @param {Object} options - 显示选项
 */
export function showValidationErrors(errors, options = {}) {
  const {
    useNotification = false, // 是否使用通知而不是消息
    maxErrors = 3, // 最多显示的错误数量
    duration = 5000, // 显示持续时间
  } = options

  if (!errors || errors.length === 0) {
    return
  }

  // 限制显示的错误数量
  const displayErrors = errors.slice(0, maxErrors)
  const hasMoreErrors = errors.length > maxErrors

  if (useNotification) {
    // 使用通知显示多个错误
    const errorList = displayErrors.map((error) => error.friendlyMessage).join('\n')
    const title = '表单验证失败'
    const message = hasMoreErrors
      ? `${errorList}\n... 还有${errors.length - maxErrors}个错误`
      : errorList

    ElNotification.error({
      title,
      message,
      duration,
      dangerouslyUseHTMLString: false,
    })
  } else {
    // 使用消息显示第一个错误
    const firstError = displayErrors[0]
    const message = hasMoreErrors
      ? `${firstError.friendlyMessage}（还有${errors.length - 1}个错误）`
      : firstError.friendlyMessage

    ElMessage.error({
      message,
      duration,
    })
  }
}

/**
 * 处理HTTP错误响应
 * @param {Object} error - Axios错误对象
 * @returns {string} 处理后的错误消息
 */
export function handleHttpError(error) {
  if (!error.response) {
    return '网络连接失败，请检查网络'
  }

  const { status, data } = error.response

  switch (status) {
    case 422: {
      // 解析验证错误
      const validationErrors = parse422ValidationErrors(data)
      if (validationErrors.length > 0) {
        // 显示友好的验证错误
        showValidationErrors(validationErrors, { useNotification: validationErrors.length > 1 })
        // 返回第一个错误作为主要错误消息
        return validationErrors[0].friendlyMessage
      }
      return data?.message || '参数验证失败'
    }

    case 400:
      return data?.message || '请求参数错误'
    case 401:
      return '登录已过期，请重新登录'
    case 403:
      return '没有权限访问'
    case 404:
      return '请求的资源不存在'
    case 500:
      return '服务器内部错误'
    default:
      return data?.message || data?.msg || data?.error || `请求失败 (${status})`
  }
}

// ========== 全局错误处理系统 ==========

// 错误类型枚举
export const ERROR_TYPES = {
  NETWORK: 'network',
  API: 'api',
  DATA: 'data',
  VALIDATION: 'validation',
  PERMISSION: 'permission',
  UNKNOWN: 'unknown',
}

// 错误级别枚举
export const ERROR_LEVELS = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical',
}

/**
 * 判断错误类型
 */
export const getErrorType = (error) => {
  if (!error) return ERROR_TYPES.UNKNOWN

  // 网络错误
  if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
    return ERROR_TYPES.NETWORK
  }

  // API错误
  if (error.response) {
    const status = error.response.status
    if (status === 403 || status === 401) {
      return ERROR_TYPES.PERMISSION
    }
    return ERROR_TYPES.API
  }

  // 数据错误
  if (error.message?.includes('data') || error.message?.includes('parse')) {
    return ERROR_TYPES.DATA
  }

  return ERROR_TYPES.UNKNOWN
}

export const isNetworkError = (error) => getErrorType(error) === ERROR_TYPES.NETWORK

/**
 * 显示用户友好的错误提示
 */
const showUserFriendlyError = (context, errorType, customMessage = null) => {
  let message = customMessage

  if (!message) {
    switch (errorType) {
      case ERROR_TYPES.NETWORK:
        message = `${context}失败：网络连接异常，请检查网络后重试`
        break
      case ERROR_TYPES.PERMISSION:
        message = `${context}失败：权限不足，请联系管理员`
        break
      case ERROR_TYPES.DATA:
        message = `${context}失败：数据获取异常，请刷新页面重试`
        break
      default:
        message = `${context}失败：服务异常，请稍后重试`
    }
  }

  const throttleKey = `${errorType}:${context}:${message}`
  if (!shouldDisplayError(throttleKey)) return

  if (errorType === ERROR_TYPES.PERMISSION || errorType === ERROR_TYPES.NETWORK) {
    ElNotification({ title: '操作失败', message, type: 'error', duration: 5000 })
  } else {
    ElMessage({ message, type: 'warning', duration: 3000 })
  }
}

/**
 * 数据获取错误的专用处理函数
 * @param {Error} error - 错误对象
 * @param {string} dataType - 数据类型（如：机构数据、角色数据等）
 * @param {*} fallbackValue - 失败时的回退值
 * @returns {*} 回退值
 */
export const handleDataFetchError = (error, dataType, fallbackValue = []) => {
  const errorType = getErrorType(error)

  // 开发环境输出详细错误
  const isDev = (import.meta?.env?.MODE === 'development') || (import.meta?.env?.DEV === true)
  if (isDev) {
    console.group(`🚨 数据获取失败 - ${dataType}`)
    console.error('错误对象:', error)
    console.error('错误类型:', errorType)
    console.error('回退值:', fallbackValue)
    console.groupEnd()
  } else {
    console.error(`获取${dataType}失败:`, error?.message || error)
  }

  // 避免与 HTTP 拦截器的网络错误提示重复：网络类错误在拦截器里统一提示，这里静默
  if (errorType !== ERROR_TYPES.NETWORK) {
    showUserFriendlyError(`获取${dataType}`, errorType)
  }

  return fallbackValue
}
