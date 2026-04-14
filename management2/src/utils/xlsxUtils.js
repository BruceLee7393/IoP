// xlsx 工具库 - 按需加载
let xlsx = null

/**
 * 按需加载 xlsx 库
 * @returns {Promise<Object>} xlsx 库对象
 */
export const loadXlsx = async () => {
  if (!xlsx) {
    try {
      xlsx = await import('xlsx')
    } catch (error) {
      console.error('加载 xlsx 库失败:', error)
      throw new Error('Excel 处理库加载失败')
    }
  }
  return xlsx
}

/**
 * 读取 Excel 文件
 * @param {File} file - Excel 文件
 * @param {Object} options - 读取选项
 * @returns {Promise<Array>} 解析后的数据
 */
export const readExcelFile = async (file, options = {}) => {
  const XLSX = await loadXlsx()

  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const sheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[sheetName]

        // 转换为 JSON 数组
        const jsonData = XLSX.utils.sheet_to_json(worksheet, options)
        resolve(jsonData)
      } catch (error) {
        reject(new Error('Excel 文件解析失败'))
      }
    }

    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }

    reader.readAsArrayBuffer(file)
  })
}

/**
 * 生成 Excel 文件
 * @param {Array} data - 数据数组
 * @param {string} sheetName - 工作表名称
 * @param {Object} options - 生成选项
 * @returns {Blob} Excel 文件 blob
 */
export const generateExcelFile = async (data, sheetName = 'Sheet1', options = {}) => {
  const XLSX = await loadXlsx()

  try {
    // 创建工作表
    const worksheet = XLSX.utils.json_to_sheet(data, options)

    // 创建工作簿
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)

    // 生成 blob
    const excelBuffer = XLSX.write(workbook, {
      bookType: 'xlsx',
      type: 'array'
    })

    return new Blob([excelBuffer], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
  } catch (error) {
    throw new Error('Excel 文件生成失败')
  }
}

/**
 * 下载 Excel 文件
 * @param {Array} data - 数据数组
 * @param {string} filename - 文件名
 * @param {Object} options - 选项
 */
export const downloadExcelFile = async (data, filename, options = {}) => {
  try {
    const blob = await generateExcelFile(data, 'Sheet1', options)

    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.style.display = 'none'

    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    // 释放 URL
    window.URL.revokeObjectURL(url)
  } catch (error) {
    throw new Error('Excel 文件下载失败')
  }
}
