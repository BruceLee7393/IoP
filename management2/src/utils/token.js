// src/utils/token.js
/**
 * JWT令牌管理工具
 */
const safeParse = (str, defaultVal = null) => {
  if (!str || str === 'undefined') return defaultVal
  try {
    return JSON.parse(str)
  } catch {
    return defaultVal
  }
}

const TOKEN_KEY = 'authToken'
const REFRESH_TOKEN_KEY = 'refreshToken'
const USER_INFO_KEY = 'userInfo'

/**
 * 获取访问令牌
 * @returns {string|null}
 */
export function getToken() {
  const token = localStorage.getItem(TOKEN_KEY)
  // console.log('getToken调用，返回:', token ? 'token存在' : 'token不存在')
  return token
}

/**
 * 设置访问令牌
 * @param {string} token
 */
export function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
    // console.log('setToken调用，已保存token')
  } else {
    // console.warn('setToken调用，但token为空')
  }
}

/**
 * 移除访问令牌
 */
export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
  // console.log('removeToken调用，已移除token')
}

/**
 * 获取刷新令牌
 * @returns {string|null}
 */
export function getRefreshToken() {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
  // console.log(
  //   'getRefreshToken调用，返回:',
  //   refreshToken ? 'refreshToken存在' : 'refreshToken不存在',
  // )
  return refreshToken
}

/**
 * 设置刷新令牌
 * @param {string} refreshToken
 */
export function setRefreshToken(refreshToken) {
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    // console.log('setRefreshToken调用，已保存refreshToken')
  } else {
    // console.warn('setRefreshToken调用，但refreshToken为空')
  }
}

/**
 * 移除刷新令牌
 */
export function removeRefreshToken() {
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  // console.log('removeRefreshToken调用，已移除refreshToken')
}

/**
 * 获取用户信息
 * @returns {object|null}
 */
export function getUserInfo() {
  const userInfoStr = localStorage.getItem(USER_INFO_KEY)
  // console.log('getUserInfo调用，原始字符串:', userInfoStr)

  const userInfo = safeParse(userInfoStr)
  // console.log('getUserInfo调用，解析结果:', userInfo)

  return userInfo
}

/**
 * 设置用户信息
 * @param {object} userInfo
 */
export function setUserInfo(userInfo) {
  if (userInfo) {
    const userInfoStr = JSON.stringify(userInfo)
    localStorage.setItem(USER_INFO_KEY, userInfoStr)
    // console.log('setUserInfo调用，已保存用户信息:', userInfo)
    // console.log('setUserInfo调用，保存的字符串:', userInfoStr)

    // 验证保存是否成功
    const verification = localStorage.getItem(USER_INFO_KEY)
    // console.log('setUserInfo验证，保存后立即读取:', verification)
  } else {
    console.warn('setUserInfo调用，但userInfo为空:', userInfo)
  }
}

/**
 * 移除用户信息
 */
export function removeUserInfo() {
  localStorage.removeItem(USER_INFO_KEY)
  // console.log('removeUserInfo调用，已移除用户信息')
}

/**
 * 清除所有认证信息
 */
export function clearAuth() {
  removeToken()
  removeRefreshToken()
  removeUserInfo()
  // console.log('clearAuth调用，已清除所有认证信息')
}

/**
 * 检查令牌是否存在
 * @returns {boolean}
 */
export function hasToken() {
  return !!getToken()
}

/**
 * 解析JWT令牌（不验证签名，仅用于获取payload信息）
 * @param {string} token
 * @returns {object|null}
 */
export function parseToken(token) {
  if (!token) return null
  try {
    const parts = token.split('.')
    // 非JWT格式（不含三段）的令牌，直接返回null，由调用方决定如何处理
    if (parts.length !== 3) return null
    const payload = parts[1]
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
    return safeParse(decoded) // ← 这里也兜底
  } catch {
    return null
  }
}

/**
 * 粗略判断是否为JWT（仅用于调试日志，不做安全判断）
 * @param {string} token
 * @returns {boolean}
 */
export function isLikelyJwt(token) {
  if (!token) return false
  const parts = token.split('.')
  if (parts.length !== 3) return false
  try {
    const payloadObj = parseToken(token)
    // 只要能解析出对象即可视为JWT；若包含exp更可信
    return !!payloadObj
  } catch {
    return false
  }
}

/**
 * 检查令牌是否即将过期（提前5分钟）
 * @param {string} token
 * @returns {boolean}
 */
export function isTokenExpiringSoon(token) {
  if (!token) return true

  const payload = parseToken(token)
  // 对于非JWT或无exp的令牌，认为不存在“即将过期”的概念，返回false
  if (!payload || !payload.exp) {
    return false
  }

  const expirationTime = payload.exp * 1000 // 转换为毫秒
  const currentTime = Date.now()
  const fiveMinutes = 5 * 60 * 1000 // 5分钟

  const willExpireSoon = expirationTime - currentTime < fiveMinutes
  console.log('Token过期检查:', {
    currentTime: new Date(currentTime).toISOString(),
    expirationTime: new Date(expirationTime).toISOString(),
    willExpireSoon,
  })

  return willExpireSoon
}

/**
 * 检查令牌是否已过期
 * @param {string} token
 * @returns {boolean}
 */
export function isTokenExpired(token) {
  if (!token) {
    // console.log('Token为空，视为已过期')
    return true
  }

  const payload = parseToken(token)
  // 对于非JWT或无exp的令牌，视为“不过期”（由后端在401时驱逐）
  if (!payload || !payload.exp) {
    return false
  }

  const expirationTime = payload.exp * 1000
  const currentTime = Date.now()
  const isExpired = currentTime >= expirationTime

  // console.log('Token过期检查:', {
  //   currentTime: new Date(currentTime).toISOString(),
  //   expirationTime: new Date(expirationTime).toISOString(),
  //   isExpired,
  // })

  return isExpired
}
