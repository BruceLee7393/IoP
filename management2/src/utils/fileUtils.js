// src/utils/fileUtils.js
import { ElMessage } from 'element-plus'

/**
 * 文件下载工具函数
 */

/**
 * 通用文件下载函数
 * @param {string} url - 下载URL
 * @param {string} filename - 文件名
 * @param {Object} options - 选项
 */
export const downloadFile = async (url, filename, options = {}) => {
  try {
    const {
      method = 'GET',
      headers = {},
      showProgress = false,
      onProgress = null
    } = options

    // 创建下载请求
    const response = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        ...headers
      }
    })

    if (!response.ok) {
      throw new Error(`下载失败: ${response.status} ${response.statusText}`)
    }

    // 获取文件大小
    const contentLength = response.headers.get('content-length')
    const total = contentLength ? parseInt(contentLength, 10) : 0

    // 读取响应流
    const reader = response.body.getReader()
    const chunks = []
    let received = 0

    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      chunks.push(value)
      received += value.length

      // 进度回调
      if (showProgress && onProgress && total > 0) {
        const progress = Math.round((received / total) * 100)
        onProgress(progress)
      }
    }

    // 合并数据
    const blob = new Blob(chunks)
    
    // 创建下载链接
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(downloadUrl)

    return { success: true, filename }
  } catch (error) {
    console.error('文件下载失败:', error)
    throw error
  }
}

/**
 * 从响应头获取文件名
 * @param {Response} response - HTTP响应对象
 * @param {string} defaultName - 默认文件名
 * @returns {string} 文件名
 */
export const getFilenameFromResponse = (response, defaultName = 'download') => {
  const contentDisposition = response.headers.get('content-disposition')
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
    if (filenameMatch && filenameMatch[1]) {
      return filenameMatch[1].replace(/['"]/g, '')
    }
  }
  return defaultName
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的文件大小
 */
export const formatFileSize = (bytes) => {
  if (!bytes && bytes !== 0) return '-'
  if (bytes === 0) return '0 B'
  
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 验证文件类型
 * @param {File} file - 文件对象
 * @param {Array} allowedTypes - 允许的文件类型数组
 * @returns {boolean} 是否为允许的文件类型
 */
export const validateFileType = (file, allowedTypes = []) => {
  if (!file || !allowedTypes.length) return true
  
  const fileName = file.name.toLowerCase()
  return allowedTypes.some(type => fileName.endsWith(`.${type.toLowerCase()}`))
}

/**
 * 验证文件大小
 * @param {File} file - 文件对象
 * @param {number} maxSize - 最大文件大小（字节）
 * @returns {boolean} 是否在允许的大小范围内
 */
export const validateFileSize = (file, maxSize) => {
  if (!file || !maxSize) return true
  return file.size <= maxSize
}

/**
 * 获取文件扩展名
 * @param {string} filename - 文件名
 * @returns {string} 文件扩展名
 */
export const getFileExtension = (filename) => {
  if (!filename) return ''
  const lastDotIndex = filename.lastIndexOf('.')
  return lastDotIndex !== -1 ? filename.slice(lastDotIndex + 1).toLowerCase() : ''
}

/**
 * 生成唯一文件名
 * @param {string} originalName - 原始文件名
 * @returns {string} 唯一文件名
 */
export const generateUniqueFilename = (originalName) => {
  const timestamp = Date.now()
  const random = Math.random().toString(36).substring(2, 8)
  const extension = getFileExtension(originalName)
  const nameWithoutExt = originalName.replace(/\.[^/.]+$/, '')
  
  return `${nameWithoutExt}_${timestamp}_${random}${extension ? '.' + extension : ''}`
}

/**
 * 压缩文件类型常量
 */
export const ARCHIVE_TYPES = ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz']

/**
 * 图片文件类型常量
 */
export const IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']

/**
 * 文档文件类型常量
 */
export const DOCUMENT_TYPES = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']

/**
 * 检查是否为压缩文件
 * @param {string} filename - 文件名
 * @returns {boolean} 是否为压缩文件
 */
export const isArchiveFile = (filename) => {
  const ext = getFileExtension(filename)
  return ARCHIVE_TYPES.includes(ext)
}

/**
 * 检查是否为图片文件
 * @param {string} filename - 文件名
 * @returns {boolean} 是否为图片文件
 */
export const isImageFile = (filename) => {
  const ext = getFileExtension(filename)
  return IMAGE_TYPES.includes(ext)
}

/**
 * 检查是否为文档文件
 * @param {string} filename - 文件名
 * @returns {boolean} 是否为文档文件
 */
export const isDocumentFile = (filename) => {
  const ext = getFileExtension(filename)
  return DOCUMENT_TYPES.includes(ext)
}

/**
 * 文件上传进度处理器
 */
export class UploadProgressHandler {
  constructor(onProgress = null, onComplete = null, onError = null) {
    this.onProgress = onProgress
    this.onComplete = onComplete
    this.onError = onError
    this.startTime = null
    this.loaded = 0
    this.total = 0
  }

  start(total = 0) {
    this.startTime = Date.now()
    this.total = total
    this.loaded = 0
  }

  update(loaded) {
    this.loaded = loaded
    const progress = this.total > 0 ? Math.round((loaded / this.total) * 100) : 0
    const elapsed = Date.now() - this.startTime
    const speed = elapsed > 0 ? (loaded / elapsed) * 1000 : 0 // bytes per second
    
    if (this.onProgress) {
      this.onProgress({
        progress,
        loaded,
        total: this.total,
        speed,
        elapsed
      })
    }
  }

  complete() {
    if (this.onComplete) {
      this.onComplete({
        loaded: this.loaded,
        total: this.total,
        elapsed: Date.now() - this.startTime
      })
    }
  }

  error(error) {
    if (this.onError) {
      this.onError(error)
    }
  }
}
