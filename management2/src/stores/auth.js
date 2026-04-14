// src/stores/auth.js
import { defineStore } from 'pinia'
import * as authApi from '@/api/auth'
import { usePermissionStore } from '@/stores/permission'
import { getCurrentUserInfo } from '@/api/user'
import {
  getToken,
  setToken,
  getUserInfo,
  setUserInfo,
  getRefreshToken,
  setRefreshToken,
  clearAuth,
  isTokenExpired,
  isLikelyJwt,
} from '@/utils/token'


export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    refreshToken: null,
    user: null,
    loginLoading: false,
    initialized: false,
  }),

  getters: {
    isLoggedIn: (state) => {
      if (!state.initialized) return false
      const result = !!state.token && !isTokenExpired(state.token)
      return result
    },
  },

  actions: {
    async login(credentials) {
      this.loginLoading = true
      try {
        // 正常登录流程
        const result = await authApi.login(credentials)

        this.token = result.token
        this.refreshToken = result.refreshToken
        this.user = result.userInfo
        this.initialized = true

        if (result.token) setToken(result.token);
        if (result.refreshToken) setRefreshToken(result.refreshToken);
        if (result.userInfo) setUserInfo(result.userInfo);

        // 登录后重置权限系统，确保后续重新初始化权限与导航
        try {
          const permissionStore = usePermissionStore()
          permissionStore.resetPermissions()
        } catch (e) {
          // 忽略重置失败
        }

        // 若用户信息缺少展示字段，尝试补充获取 /users/me
        try {
          const lacksName = !this.user || (!this.user.full_name && !this.user.account)
          if (lacksName) {
            const res = await getCurrentUserInfo()
            const latestUser = res.data || res
            if (latestUser) {
              this.user = latestUser
              setUserInfo(latestUser)
            }
          }
        } catch (_) {}

        return true
      } catch (error) {
        this.clearAuthState(); // 登录失败时也清理状态
        throw error
      } finally {
        this.loginLoading = false
      }
    },

    async logout() {
      try {
        await authApi.logout()
      } catch (error) {
        console.warn('后端登出失败:', error)
      } finally {
        this.clearAuthState()
        try {
          const permissionStore = usePermissionStore()
          permissionStore.resetPermissions()
        } catch (e) {}
      }
    },

    async refreshAccessToken() {
      if (!this.refreshToken) {
        throw new Error('没有刷新令牌')
      }
      try {
        const result = await authApi.refreshToken(this.refreshToken)
        this.token = result.token
        setToken(result.token)
        if (result.refreshToken) {
          this.refreshToken = result.refreshToken
          setRefreshToken(result.refreshToken)
        }
        return true
      } catch (error) {
        await this.logout()
        throw error
      }
    },

    clearAuthState() {
      this.token = null
      this.refreshToken = null
      this.user = null
      this.initialized = true
      clearAuth()
    },

    // 初始化认证状态 - 从localStorage恢复登录状态
    async initAuth() {
      console.log('🔄 初始化认证状态...')

      // 正常初始化流程
      // 标记为已初始化，防止重复调用
      this.initialized = true;

      const token = getToken();
      const user = getUserInfo();
      const refreshToken = getRefreshToken();

      console.log('🔍 从localStorage获取的数据:', {
        hasToken: !!token,
        hasUser: !!user,
        hasRefreshToken: !!refreshToken
      })

      if (token) {
        const looksJwt = isLikelyJwt(token)
        console.log(`🔐 Token形态判定: ${looksJwt ? '这是 JWT' : '不是 JWT（不透明 token）'}`)
      }

      // 如果没有token或用户信息，标记为未登录状态（不抛出错误）
      if (!token || !user) {
        console.log('❌ 没有token或用户信息，标记为未登录状态')
        this.clearAuthState();
        return false;
      }

      // 检查token是否过期
      if (isTokenExpired(token)) {
        console.log('⚠️ token已过期')
        if (refreshToken) {
          try {
            console.log('🔄 尝试刷新token...')
            this.refreshToken = refreshToken;
            await this.refreshAccessToken();
            this.user = getUserInfo();
            console.log('✅ token刷新成功')
            return true;
          } catch (refreshError) {
            console.log('❌ token刷新失败:', refreshError)
            this.clearAuthState();
            return false;
          }
        } else {
          console.log('❌ token已过期且无刷新令牌')
          this.clearAuthState();
          return false;
        }
      }

      // token有效，恢复登录状态
      this.token = token;
      this.user = user;
      this.refreshToken = refreshToken;
      console.log(`✅ 登录状态恢复成功，用户: ${user?.full_name || user?.account}`);

      // 如果本地存储的用户信息缺少展示字段，尝试补充获取
      try {
        const lacksName = !this.user || (!this.user.full_name && !this.user.account)
        if (lacksName) {
          const res = await getCurrentUserInfo()
          const latestUser = res.data || res
          if (latestUser) {
            this.user = latestUser
            setUserInfo(latestUser)
          }
        }
      } catch (_) {}
      return true;
    },
  },
})
