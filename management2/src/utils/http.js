// src/utils/http.js
import axios from 'axios'
import { ElMessage, ElNotification } from 'element-plus'
import { getToken, removeToken, isTokenExpired } from './token'
import { handleHttpError } from './errorHandler'
import Logger from './logger'


// 创建 axios 实例 - 统一使用真实后端
const http = axios.create({

  // baseURL: 'http://192.168.1.16:5000/api/',
  // baseURL: ' http://127.0.0.1:5000/api',
  // baseURL: 'http://8.138.234.158/api/',
  // baseURL: 'http://100.74.58.99:5000/api/',
  baseURL: 'http://183.169.121.226//api/',
  // baseURL: '/api/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 错误提示节流，避免后端宕机时弹窗刷屏
const ERROR_THROTTLE_MS = 4000
const errorTimestamps = new Map()
const shouldShowError = (key, throttleMs = ERROR_THROTTLE_MS) => {
  const now = Date.now()
  const last = errorTimestamps.get(key) || 0
  if (now - last > throttleMs) {
    errorTimestamps.set(key, now)
    return true
  }
  return false
}

// 不需要令牌的接口白名单
// 注意：'/users/register' 是后台管理创建用户接口，需要携带管理员Token，不能放在白名单
const NO_TOKEN_URLS = ['/auth/login', '/auth/refresh']

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    Logger.http(config.method?.toUpperCase() || 'GET', config.url,
      config.data instanceof FormData ? 'FormData' : config.data)

    // 如果是FormData，确保不设置Content-Type
    if (config.data instanceof FormData) {
      Logger.debug('HTTP请求拦截器 - 检测到FormData，移除Content-Type头')
      delete config.headers['Content-Type']
    }



    // 生产模式：正常处理
    // 检查是否为白名单接口
    const isNoTokenUrl = NO_TOKEN_URLS.some((url) => config.url?.includes(url))

    if (!isNoTokenUrl) {
      // 添加认证token
      const token = getToken()

      if (token) {
        // 检查令牌是否过期 - 但不在这里处理过期逻辑
        if (isTokenExpired(token)) {
          // console.log('HTTP请求拦截器 - Token已过期，但继续发送请求让响应拦截器处理')
          // 不要在这里清除token或跳转，让响应拦截器或store来处理
        }
        config.headers.Authorization = `Bearer ${token}`
        // console.log(
        //   'HTTP请求拦截器 - 已添加Authorization头:',
        //   config.headers.Authorization?.substring(0, 20) + '...',
        // )
      } else {
        // console.log('HTTP请求拦截器 - 无Token，跳过认证头')
      }
    } else {
      // console.log('HTTP请求拦截器 - 白名单接口，跳过认证头')
    }

    return config
  },
  (error) => {
    Logger.error('HTTP请求拦截器错误:', error)
    return Promise.reject(error)
  },
)

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    Logger.info('HTTP响应拦截器 - 响应成功:', response.config.url)

    // 如果是blob类型响应（文件下载），直接返回
    if (response.config.responseType === 'blob') {
      return response
    }

    // 自动处理后端标准响应格式
    if (response.data && typeof response.data === 'object') {
      const backendData = response.data

      // 情况1：检查是否为标准的分页列表响应格式
      if (
        backendData.code === 0 &&
        backendData.data &&
        backendData.data.items &&
        backendData.data.pagination
      ) {
        const { items, pagination } = backendData.data

        // 自动转换为前端期望的格式
        response.data = {
          records: items || [],
          total: pagination?.total || 0,
          currentPage: pagination?.page || 1,
          pageSize: pagination?.per_page || 10,
          totalPages: pagination?.pages || 1,
        }

        // console.log('HTTP响应拦截器 - 自动转换分页数据格式:', response.data)
        return response
      }

      // 情况2：检查是否为后端错误响应（有code字段且不为0）
      if (backendData.code !== undefined && backendData.code !== 0) {
        // 对于登录等特殊接口，如果HTTP状态码是200，则不视为错误
        const isSpecialEndpoint =
          response.config.url?.includes('/auth/') ||
          response.config.url?.includes('/login') ||
          response.config.url?.includes('/register')

        if (!isSpecialEndpoint || response.status !== 200) {
          // 将后端错误转换为Promise rejection，让错误拦截器处理
          const error = new Error(backendData.message || '请求失败')
          error.response = response
          error.response.data = backendData
          throw error
        }
      }

      // 情况3：检查是否为成功的单一数据响应（有code字段且为0）
      if (backendData.code === 0 && backendData.data) {
        // 对于非分页数据，提取data字段的内容
        response.data = backendData.data
        Logger.debug('HTTP响应拦截器 - 提取单一数据格式:', response.data)
        return response
      }

      // 情况4：HTTP 200状态码但没有code字段的响应（直接返回数据）
      // 这种情况下，认为响应本身就是有效数据，不做处理
      Logger.debug('HTTP响应拦截器 - 保持原始响应格式:', response.data)
    }

    return response
  },
  async (error) => {
    Logger.error('HTTP响应拦截器捕获错误:', error)



    if (error.response) {
      const { status, data } = error.response
      Logger.error('HTTP错误响应:', { status, data })

      // 特殊处理401错误
      if (status === 401) {
        // 清除所有认证信息，但不立即跳转
        removeToken()
        // console.log('HTTP拦截器：401错误，已清除token')

        // 只有在非登录页面时才跳转，避免重复跳转
        if (window.location.pathname !== '/login') {
          // 使用setTimeout延迟跳转，避免与路由守卫冲突
          setTimeout(() => {
            if (window.location.pathname !== '/login') {
              // console.log('HTTP拦截器：延迟跳转到登录页')
              window.location.href = '/login'
            }
          }, 100)
        }
        return Promise.reject(error)
      }

      // 特殊处理Blob格式的错误响应
      if (data instanceof Blob && status >= 400) {
        try {
          // 尝试将Blob转换为JSON
          const text = await data.text()
          const jsonData = JSON.parse(text)

          // 替换error.response.data为解析后的JSON数据
          error.response.data = jsonData
          Logger.debug('HTTP拦截器 - Blob错误响应已转换为JSON:', jsonData)
        } catch (parseError) {
          Logger.error('HTTP拦截器 - 无法解析Blob错误响应:', parseError)
          // 如果无法解析，使用默认错误消息
          error.response.data = { message: '请求处理失败' }
        }
      }

      // 使用新的错误处理逻辑
      const message = handleHttpError(error)
      Logger.error('HTTP拦截器最终错误信息:', message)

      // 对于以下错误类型，不在HTTP拦截器中显示，让业务组件自己处理：
      // - 422: 验证错误，已经在handleHttpError中显示了
      // - 401: 认证错误，已经在上面处理了
      // - 400: 业务错误（如订单号重复），让业务组件显示具体错误
      if (status !== 422 && status !== 401 && status !== 400) {
        const key = `${status}:${message}`
        if (shouldShowError(key)) {
          ElMessage.error(message)
        }
      }
    } else if (error.request) {
      // 典型场景：后端宕机 / CORS 限制 / 断网
      const message = '服务不可用或网络异常，请稍后重试'
      Logger.error('HTTP拦截器最终错误信息:', message)
      if (shouldShowError('network')) {
        ElNotification.error({
          title: '无法连接服务器',
          message,
          duration: 5000,
        })
      }
    } else if (error.message) {
      // 兜底 - 也进行节流
      Logger.error('HTTP拦截器最终错误信息:', error.message)
      if (shouldShowError(`msg:${error.message}`)) {
        ElMessage.error(error.message)
      }
    }

    return Promise.reject(error)
  },
)

// 通用请求方法
export const request = {
  get(url, params = {}, config = {}) {
    return http.get(url, { params, ...config })
  },

  post(url, data = {}, config = {}) {
    // 如果是FormData，不设置Content-Type，让浏览器自动设置
    if (data instanceof FormData) {
      const headers = { ...config.headers }
      delete headers['Content-Type'] // 删除可能存在的Content-Type
      config = { ...config, headers }
    }
    return http.post(url, data, config)
  },

  put(url, data = {}, config = {}) {
    return http.put(url, data, config)
  },

  patch(url, data = {}, config = {}) {
    return http.patch(url, data, config)
  },

  delete(url, config = {}) {
    return http.delete(url, config)
  },
}

export default http
