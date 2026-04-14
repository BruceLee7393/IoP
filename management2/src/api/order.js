// src/api/order.js
import { request } from '@/utils/http'
import { createGetListMethod, createExportMethod } from '@/utils/apiUtils'

// --- 订单管理 API ---

// 字段映射配置 - 根据后端schema定义
const ORDER_FIELD_MAPPING = {
  page: 'page',
  pageSize: 'per_page',
  sortBy: 'sort_by',
  order: 'sort_order',
  order_number: 'order_number',
  model: 'model',
  part_number: 'part_number',
  serial_number: 'serial_number',
  component_part_number: 'component_part_number',
  sub_component_part_number: 'sub_component_part_number',
}

// 使用通用方法创建订单列表API
export const getOrderList = createGetListMethod('/orders', ORDER_FIELD_MAPPING)

// 导出订单数据 - 使用通用方法
export const exportOrders = createExportMethod(
  '/orders/export',
  ORDER_FIELD_MAPPING,
  'order_export.xlsx',
  '订单数据导出',
)



// 获取订单详情
export const getOrderDetails = (orderId) => request.get(`/orders/${orderId}`)

// 新增订单
export const createOrder = (orderData) => request.post('/orders', orderData)

// 更新订单
export const updateOrder = (orderId, orderData) => request.put(`/orders/${orderId}`, orderData)

// 删除订单（逻辑删除）
export const deleteOrder = (orderId) => request.delete(`/orders/${orderId}`)

// 批量删除订单 - 注意：后端没有提供批量删除接口，这里保留接口但可能需要循环调用单个删除
export const batchDeleteOrders = async (orderIds) => {
  // 由于后端没有批量删除接口，我们循环调用单个删除
  const results = await Promise.allSettled(
    orderIds.map(id => deleteOrder(id))
  )

  const failed = results.filter(result => result.status === 'rejected')
  if (failed.length > 0) {
    throw new Error(`批量删除失败，${failed.length}个订单删除失败`)
  }

  return { message: '批量删除成功' }
}

// --- 批量导入相关 API ---

// 下载订单导入模板
export const downloadOrderImportTemplate = async () => {
  try {
    const response = await request.get('/orders/import/template', {}, {
      responseType: 'blob'
    })

    // 从响应头获取文件名
    const contentDisposition = response.headers['content-disposition'] || response.headers['Content-Disposition']
    let filename = 'order_import_template.xlsx'

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1]
      }
    }

    // 创建下载链接
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    return { success: true, filename }
  } catch (error) {
    console.error('下载模板失败:', error)
    throw error
  }
}

// 上传并验证订单导入文件
export const uploadOrderImportFile = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await request.post('/orders/import', formData, {
      responseType: 'blob'
    })

    // 检查响应类型
    const contentType = response.headers['content-type'] || response.headers['Content-Type']

    console.log('📦 导入响应 Content-Type:', contentType) // 调试日志

    // 如果返回的是 JSON（全部导入成功）
    if (contentType && contentType.includes('application/json')) {
      const text = await response.data.text()
      const result = JSON.parse(text)
      console.log('✅ JSON响应（全部成功）:', result) // 调试日志
      return {
        success: true,
        type: 'SUCCESS',
        data: result,
        message: result.message || '导入成功',
        success_count: result.success_count || 0,
        error_count: 0
      }
    }

    // 如果返回的是 Excel 文件（有错误，可能是全部失败或部分成功）
    if (contentType && contentType.includes('spreadsheet')) {
      const blob = new Blob([response.data])
      const contentDisposition = response.headers['content-disposition'] || response.headers['Content-Disposition']
      let filename = `order_import_errors_${Date.now()}.xlsx`

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1]
        }
      }

      // 尝试从响应头中获取成功数量（如果后端支持）
      const successCountHeader = response.headers['x-success-count'] || response.headers['X-Success-Count']
      const errorCountHeader = response.headers['x-error-count'] || response.headers['X-Error-Count']
      const totalCountHeader = response.headers['x-total-count'] || response.headers['X-Total-Count']
      
      const success_count = successCountHeader ? parseInt(successCountHeader) : 0
      const error_count = errorCountHeader ? parseInt(errorCountHeader) : 0
      const total_count = totalCountHeader ? parseInt(totalCountHeader) : 0

      console.log('📊 Excel响应头统计:', { 
        success_count, 
        error_count, 
        total_count,
        headers: {
          'X-Success-Count': successCountHeader,
          'X-Error-Count': errorCountHeader,
          'X-Total-Count': totalCountHeader
        }
      }) // 调试日志

      // 判断是部分成功还是全部失败
      const isPartialSuccess = success_count > 0

      console.log(`${isPartialSuccess ? '⚠️' : '❌'} 判断结果: ${isPartialSuccess ? 'PARTIAL_SUCCESS' : 'ERROR'}`) // 调试日志

      return {
        success: isPartialSuccess,
        type: isPartialSuccess ? 'PARTIAL_SUCCESS' : 'ERROR',
        hasErrorFile: true,
        blob: blob,
        filename: filename,
        success_count: success_count,
        error_count: error_count,
        total_count: total_count,
        message: isPartialSuccess 
          ? `部分导入成功：${success_count}条成功，${error_count}条失败` 
          : '导入失败，请下载错误文件查看详情'
      }
    }

    throw new Error('未知的响应类型')
  } catch (error) {
    console.error('上传导入文件失败:', error)

    // 处理错误响应
    if (error.response && error.response.data) {
      const contentType = error.response.headers['content-type'] || error.response.headers['Content-Type']

      // 如果错误响应是 Excel 文件
      if (contentType && contentType.includes('spreadsheet')) {
        const blob = new Blob([error.response.data])
        const contentDisposition = error.response.headers['content-disposition'] || error.response.headers['Content-Disposition']
        let filename = `order_import_errors_${Date.now()}.xlsx`

        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
          if (filenameMatch && filenameMatch[1]) {
            filename = filenameMatch[1]
          }
        }

        // 尝试从响应头中获取成功数量
        const successCountHeader = error.response.headers['x-success-count'] || error.response.headers['X-Success-Count']
        const errorCountHeader = error.response.headers['x-error-count'] || error.response.headers['X-Error-Count']
        const totalCountHeader = error.response.headers['x-total-count'] || error.response.headers['X-Total-Count']
        
        const success_count = successCountHeader ? parseInt(successCountHeader) : 0
        const error_count = errorCountHeader ? parseInt(errorCountHeader) : 0
        const total_count = totalCountHeader ? parseInt(totalCountHeader) : 0

        const isPartialSuccess = success_count > 0

        return {
          success: isPartialSuccess,
          type: isPartialSuccess ? 'PARTIAL_SUCCESS' : 'ERROR',
          hasErrorFile: true,
          blob: blob,
          filename: filename,
          success_count: success_count,
          error_count: error_count,
          total_count: total_count,
          message: isPartialSuccess 
            ? `部分导入成功：${success_count}条成功，${error_count}条失败` 
            : '导入失败，请下载错误文件查看详情'
        }
      }

      // 如果错误响应是 JSON
      if (contentType && contentType.includes('application/json')) {
        try {
          const text = await error.response.data.text()
          const errorData = JSON.parse(text)
          throw new Error(errorData.error || errorData.message || '导入失败')
        } catch (parseError) {
          throw new Error('导入失败')
        }
      }
    }

    throw error
  }
}

// --- 文件上传相关 API ---

// 上传订单附件
export const uploadOrderAttachment = async (orderId, file) => {
  const formData = new FormData()
  formData.append('file', file)

  console.log('上传订单附件:', {
    orderId,
    fileName: file.name,
    fileSize: file.size,
    fileType: file.type,
  })

  try {
    const response = await request.post(`/orders/${orderId}/upload`, formData)
    console.log('订单附件上传响应:', response)
    return response.data
  } catch (error) {
    console.error('Error in uploadOrderAttachment:', error)
    if (error.response?.data?.message) {
      throw new Error(error.response.data.message)
    }
    throw error
  }
}

// 下载订单附件
export const downloadOrderAttachment = async (orderId, originalFilename = null) => {
  try {
    console.log('下载订单附件:', orderId)
    const response = await request.get(`/orders/${orderId}/download`, {}, {
      responseType: 'blob'
    })

    // 调试：打印所有响应头
    console.log('所有响应头:', response.headers)
    console.log('响应状态:', response.status)
    console.log('响应数据大小:', response.data.size)

    // 从响应头获取原始文件名
    const contentDisposition = response.headers['content-disposition'] || response.headers['Content-Disposition']
    const contentType = response.headers['content-type'] || response.headers['Content-Type']

    console.log('Content-Disposition 头:', contentDisposition)
    console.log('Content-Type 头:', contentType)

    // 根据Content-Type推断文件扩展名
    const getExtensionFromContentType = (contentType) => {
      if (!contentType) return ''
      const typeMap = {
        'application/zip': '.zip',
        'application/x-zip-compressed': '.zip',
        'application/rar': '.rar',
        'application/x-rar-compressed': '.rar',
        'application/x-7z-compressed': '.7z',
        'application/gzip': '.gz',
        'application/x-tar': '.tar',
        'application/x-gzip': '.gz'
      }
      return typeMap[contentType.toLowerCase()] || ''
    }

    // 优先使用传入的原始文件名，其次尝试从Content-Disposition解析，最后使用默认文件名
    let filename = originalFilename || `order_${orderId}_attachment${getExtensionFromContentType(contentType)}`

    // 如果没有传入原始文件名，且有Content-Disposition头，尝试解析其中的文件名
    if (!originalFilename && contentDisposition) {
      console.log('尝试解析Content-Disposition:', contentDisposition)

      // 方法1: 尝试解析标准的 filename= 格式
      let filenameMatch = contentDisposition.match(/filename=([^;]+)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '').trim()
        console.log('方法1解析成功:', filename)
      } else {
        // 方法2: 尝试解析带引号的格式
        filenameMatch = contentDisposition.match(/filename="([^"]+)"/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].trim()
          console.log('方法2解析成功:', filename)
        } else {
          // 方法3: 尝试解析 filename*= 格式（支持UTF-8编码）
          const filenameStarMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/)
          if (filenameStarMatch && filenameStarMatch[1]) {
            filename = decodeURIComponent(filenameStarMatch[1])
            console.log('方法3解析成功:', filename)
          } else {
            console.log('所有解析方法都失败，使用默认文件名:', filename)
          }
        }
      }
    } else if (originalFilename) {
      console.log('使用传入的原始文件名:', filename)
    } else {
      console.log('没有Content-Disposition头，使用默认文件名:', filename)
    }

    console.log('解析得到的文件名:', filename)

    // 创建下载链接 - 保持文件原始状态，不进行任何修改
    const blob = new Blob([response.data], {
      type: response.headers['content-type'] || response.headers['Content-Type'] || 'application/octet-stream'
    })

    console.log('Blob信息:', {
      size: blob.size,
      type: blob.type,
      originalContentType: response.headers['content-type'] || response.headers['Content-Type']
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    return { success: true, filename }
  } catch (error) {
    console.error('Error in downloadOrderAttachment:', error)
    if (error.response?.data?.message) {
      throw new Error(error.response.data.message)
    }
    throw error
  }
}

// 上传软件附件
export const uploadSoftwareAttachment = async (softwareId, file) => {
  const formData = new FormData()
  formData.append('file', file)

  console.log('上传软件附件:', {
    softwareId,
    fileName: file.name,
    fileSize: file.size,
    fileType: file.type,
  })

  try {
    const response = await request.post(`/orders/softwares/${softwareId}/upload`, formData)
    console.log('软件附件上传响应:', response)
    return response.data
  } catch (error) {
    console.error('Error in uploadSoftwareAttachment:', error)
    if (error.response?.data?.message) {
      throw new Error(error.response.data.message)
    }
    throw error
  }
}

// 下载软件附件
export const downloadSoftwareAttachment = async (softwareId, originalFilename = null) => {
  try {
    console.log('下载软件附件:', softwareId)
    const response = await request.get(`/orders/softwares/${softwareId}/download`, {}, {
      responseType: 'blob'
    })

    // 调试：打印所有响应头
    console.log('所有响应头:', response.headers)
    console.log('响应状态:', response.status)
    console.log('响应数据大小:', response.data.size)

    // 从响应头获取原始文件名
    const contentDisposition = response.headers['content-disposition'] || response.headers['Content-Disposition']
    const contentType = response.headers['content-type'] || response.headers['Content-Type']

    console.log('Content-Disposition 头:', contentDisposition)
    console.log('Content-Type 头:', contentType)

    // 根据Content-Type推断文件扩展名
    const getExtensionFromContentType = (contentType) => {
      if (!contentType) return ''
      const typeMap = {
        'application/zip': '.zip',
        'application/x-zip-compressed': '.zip',
        'application/rar': '.rar',
        'application/x-rar-compressed': '.rar',
        'application/x-7z-compressed': '.7z',
        'application/gzip': '.gz',
        'application/x-tar': '.tar',
        'application/x-gzip': '.gz'
      }
      return typeMap[contentType.toLowerCase()] || ''
    }

    // 优先使用传入的原始文件名，其次尝试从Content-Disposition解析，最后使用默认文件名
    let filename = originalFilename || `software_${softwareId}_attachment${getExtensionFromContentType(contentType)}`

    // 如果没有传入原始文件名，且有Content-Disposition头，尝试解析其中的文件名
    if (!originalFilename && contentDisposition) {
      console.log('尝试解析Content-Disposition:', contentDisposition)

      // 方法1: 尝试解析标准的 filename= 格式
      let filenameMatch = contentDisposition.match(/filename=([^;]+)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '').trim()
        console.log('方法1解析成功:', filename)
      } else {
        // 方法2: 尝试解析带引号的格式
        filenameMatch = contentDisposition.match(/filename="([^"]+)"/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].trim()
          console.log('方法2解析成功:', filename)
        } else {
          // 方法3: 尝试解析 filename*= 格式（支持UTF-8编码）
          const filenameStarMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/)
          if (filenameStarMatch && filenameStarMatch[1]) {
            filename = decodeURIComponent(filenameStarMatch[1])
            console.log('方法3解析成功:', filename)
          } else {
            console.log('所有解析方法都失败，使用默认文件名:', filename)
          }
        }
      }
    } else if (originalFilename) {
      console.log('使用传入的原始文件名:', filename)
    } else {
      console.log('没有Content-Disposition头，使用默认文件名:', filename)
    }

    console.log('解析得到的文件名:', filename)

    // 创建下载链接 - 保持文件原始状态，不进行任何修改
    const blob = new Blob([response.data], {
      type: response.headers['content-type'] || response.headers['Content-Type'] || 'application/octet-stream'
    })

    console.log('Blob信息:', {
      size: blob.size,
      type: blob.type,
      originalContentType: response.headers['content-type'] || response.headers['Content-Type']
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    return { success: true, filename }
  } catch (error) {
    console.error('Error in downloadSoftwareAttachment:', error)
    if (error.response?.data?.message) {
      throw new Error(error.response.data.message)
    }
    throw error
  }
}
