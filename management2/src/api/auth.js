// src/api/auth.js
import { request } from '@/utils/http'

/**
 * 用户登录
 * @param {Object} data 登录数据
 * @param {string} data.account 用户名
 * @param {string} data.password 密码
 * @param {string} data.captcha 验证码
 * @param {string} data.captchaId 验证码ID
 * @returns {Promise}
 */
export const login = async (data) => {
  try {
    const response = await request.post('/auth/login', data)
    console.log('登录API原始响应:', response)
    console.log('登录API响应数据:', response.data)

    const result = response.data.data || response.data
    console.log('登录API解析后的result:', result)

    // 确保返回的数据格式正确
    const loginResult = {
      token: result.token || result.access_token,
      refreshToken: result.refreshToken || result.refresh_token,
      userInfo: result.userInfo || result.user || result.userinfo || result.data || result,
      permissions: result.permissions || [],
      expiresIn: result.expiresIn || result.expires_in,
    }

    console.log('登录API最终返回结果:', loginResult)
    console.log('用户信息详情:', loginResult.userInfo)

    return loginResult
  } catch (error) {
    console.error('登录API错误:', error)
    // 重新抛出错误，保持原有的错误信息
    throw new Error(
      error.response?.data?.message || error.response?.data?.msg || error.message || '登录失败',
    )
  }
}

/**
 * 用户登出
 * @returns {Promise}
 */
export const logout = async () => {
  try {
    await request.post('/auth/logout')
  } catch (error) {
    // 登出失败不影响前端清理，只记录错误
    console.warn('登出接口调用失败:', error.message)
  }
}

/**
 * 刷新令牌
 * @param {string} refreshToken 刷新令牌
 * @returns {Promise}
 */
export const refreshToken = async (refreshToken) => {
  try {
    const response = await request.post('/auth/refresh', {
      refreshToken,
    })
    const result = response.data.data || response.data

    return {
      token: result.token || result.access_token,
      refreshToken: result.refreshToken || result.refresh_token,
      expiresIn: result.expiresIn || result.expires_in,
    }
  } catch (error) {
    throw new Error(
      error.response?.data?.message || error.response?.data?.msg || error.message || '令牌刷新失败',
    )
  }
}
