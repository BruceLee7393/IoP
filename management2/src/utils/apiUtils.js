// src/utils/apiUtils.js
// API工具库 - 消除重复的API模式代码

import { request } from '@/utils/http'

/**
 * 字段映射工具 - 将前端驼峰命名转换为后端下划线命名
 * @param {Object} params - 前端参数对象
 * @param {Object} fieldMapping - 字段映射配置
 * @returns {Object} 转换后的后端参数对象
 */
export const mapFieldsToBackend = (params = {}, fieldMapping = {}) => {
  const queryParams = {}

  // 参数转换和传递，过滤空值
  Object.keys(params).forEach((key) => {
    const backendKey = fieldMapping[key] || key
    const value = params[key]

    // 过滤空值和对象类型的值
    if (value !== undefined && value !== null && value !== '' && typeof value !== 'object') {
      queryParams[backendKey] = value
    }
  })

  return queryParams
}

/**
 * URL构建工具 - 过滤空参数并构建查询字符串
 * @param {Object} params - 参数对象
 * @returns {string} 构建的查询字符串
 */
export const buildQueryString = (params = {}) => {
  const urlParams = new URLSearchParams()

  Object.keys(params).forEach((key) => {
    const value = params[key]
    if (value !== undefined && value !== null && value !== '') {
      urlParams.append(key, value)
    }
  })

  return urlParams.toString()
}

/**
 * 通用分页参数处理
 * @param {Object} params - 原始参数
 * @returns {Object} 包含默认分页参数的对象
 */
export const ensurePaginationParams = (params = {}) => {
  const processedParams = { ...params }

  // 确保分页参数存在
  if (!processedParams.page) processedParams.page = 1
  if (!processedParams.per_page && !processedParams.pageSize) {
    processedParams.per_page = 10
  }

  return processedParams
}

/**
 * 嵌套对象数据处理工具 - 将嵌套对象的属性平铺到顶层
 * @param {Array} items - 数据项数组
 * @param {Object} nestedFieldConfig - 嵌套字段配置
 * @returns {Array} 处理后的数据数组
 *
 * 配置示例:
 * {
 *   'institution': ['institution_code', 'institution_name'],
 *   'role': ['role_name'],
 *   'device': ['device_id', 'device_type', 'firmware_version'],
 *   'device.institution': ['institution_code', 'institution_name'], // 支持多层嵌套
 *   'uploader': ['uploader_name:full_name'] // 支持别名映射 目标字段:源字段
 * }
 */
export const flattenNestedFields = (items = [], nestedFieldConfig = {}) => {
  return items.map((item) => {
    const processedItem = { ...item }

    Object.keys(nestedFieldConfig).forEach((nestedKey) => {
      const fieldsToExtract = nestedFieldConfig[nestedKey]

      // 支持多层嵌套，如 'device.institution'
      const nestedObject = getNestedValue(item, nestedKey)

      if (nestedObject && typeof nestedObject === 'object') {
        fieldsToExtract.forEach((fieldSpec) => {
          // 支持别名映射：'target_field:source_field' 或直接 'field_name'
          const [targetField, sourceField] = fieldSpec.includes(':')
            ? fieldSpec.split(':')
            : [fieldSpec, fieldSpec]

          processedItem[targetField] = nestedObject[sourceField] || ''
        })
      } else {
        // 如果嵌套对象不存在，设置默认空值
        fieldsToExtract.forEach((fieldSpec) => {
          const targetField = fieldSpec.includes(':') ? fieldSpec.split(':')[0] : fieldSpec
          if (!processedItem[targetField]) {
            processedItem[targetField] = ''
          }
        })
      }
    })

    return processedItem
  })
}

/**
 * 获取嵌套对象的值，支持多层路径如 'device.institution'
 * @param {Object} obj - 源对象
 * @param {string} path - 嵌套路径
 * @returns {any} 嵌套值
 */
const getNestedValue = (obj, path) => {
  return path.split('.').reduce((current, key) => {
    return current && current[key] !== undefined ? current[key] : null
  }, obj)
}

/**
 * 文件下载工具
 * @param {Blob} blob - 文件blob数据
 * @param {string} defaultFilename - 默认文件名
 * @param {Object} responseHeaders - 响应头
 * @param {string} timestampPrefix - 时间戳前缀（用于生成文件名）
 */
export const downloadFile = (
  blob,
  defaultFilename,
  responseHeaders = {},
  timestampPrefix = '数据导出',
) => {
  // 从响应头获取文件名
  let filename = defaultFilename
  const contentDisposition = responseHeaders['content-disposition']

  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1].replace(/['"]/g, '')
    }
  } else {
    // 使用时间戳生成文件名
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    // 根据文件类型确定扩展名
    const extension = filename.includes('.xlsx') ? '.xlsx' : '.xlsx'
    filename = `${timestampPrefix}_${timestamp}${extension}`
  }

  // 创建下载链接
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.style.display = 'none'

  // 添加到DOM，点击，然后清理
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  // 释放URL对象
  window.URL.revokeObjectURL(url)
}

/**
 * 通用getList方法生成器
 * @param {string} endpoint - API端点
 * @param {Object} fieldMapping - 字段映射配置
 * @param {Object} nestedFieldConfig - 嵌套字段配置（可选）
 * @returns {Function} getList方法
 */
// 1. createGetListMethod 改造
export const createGetListMethod = (endpoint, fieldMapping, nestedFieldConfig = null) => {
  return async (params = {}) => {
    const queryParams = mapFieldsToBackend(params, fieldMapping)
    const paginatedParams = ensurePaginationParams(queryParams)

    // 构建查询字符串并发送请求
    const queryString = buildQueryString(paginatedParams)
    const fullUrl = queryString ? `${endpoint}?${queryString}` : endpoint
    const response = await request.get(fullUrl)

    let records = (response.data && response.data.records) || []
    if (nestedFieldConfig) {
      records = flattenNestedFields(records, nestedFieldConfig)
    }
    return {
      records,
      total: response.data.total || 0,
      currentPage: response.data.currentPage || 1,
      pageSize: response.data.pageSize || 10,
      totalPages: response.data.totalPages || 1,
    }
  }
}
/**
 * 通用export方法生成器
 * @param {string} endpoint - 导出API端点
 * @param {Object} fieldMapping - 字段映射配置
 * @param {string} defaultFilename - 默认文件名
 * @param {string} timestampPrefix - 时间戳前缀
 * @returns {Function} export方法
 */
export const createExportMethod = (endpoint, fieldMapping, defaultFilename, timestampPrefix) => {
  return async (params = {}) => {
    try {
      // console.log(`${endpoint} export 原始参数:`, params)

      // 1. 字段映射和参数处理
      const queryParams = mapFieldsToBackend(params, fieldMapping)

      // console.log(`${endpoint} export 处理后参数:`, queryParams)

      // 2. 发送请求 - 使用GET方法，参数作为查询字符串
      const queryString = buildQueryString(queryParams)
      const fullUrl = queryString ? `${endpoint}?${queryString}` : endpoint

      const response = await request.get(
        fullUrl,
        {},
        {
          responseType: 'blob',
        },
      )

      // 3. 处理文件下载
      downloadFile(response.data, defaultFilename, response.headers, timestampPrefix)

      return { success: true }
    } catch (error) {
      console.error(`Error in ${endpoint} export:`, error)
      throw error
    }
  }
}
