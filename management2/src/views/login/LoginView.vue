<!-- src/views/LoginView.vue -->
<template>
  <div class="login-container">
    <div class="login-box">
      <div class="brand">
        <img class="brand-logo" :src="logoSrc" alt="Double Power Logo" />
        <span class="brand-text">Double&nbsp;Power</span>
      </div>
      <div class="login-title">产品管理系统</div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        status-icon
      >
        <!-- 账号 -->
        <el-form-item prop="account">
          <el-input
            v-model="loginForm.account"
            placeholder="登录账号"
            :prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>

        <!-- 密码 -->
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="登录密码"
            show-password
            :prefix-icon="Lock"
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <!-- 记住密码 -->
        <el-form-item>
          <el-checkbox v-model="loginForm.remember">记住密码</el-checkbox>
        </el-form-item>

        <!-- 登录按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%"
            size="large"
            :loading="loading"
            @click="handleLogin"
            >登 录</el-button
          >
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import logoSrc from '@/assets/images/logo.png'
import bgImage from '@/assets/images/login-bg.svg'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

const router = useRouter()
const authStore = useAuthStore()
const permissionStore = usePermissionStore()
const loginFormRef = ref(null)
const loading = ref(false)
const loginForm = reactive({
  account: '',
  password: '',
  remember: false,
})

const bgImageUrl = `url(${bgImage})`

const loginRules = {
  account: [
    { required: true, message: '登录账号不能为空', trigger: 'blur' },
    { min: 1, max: 32, message: '账号长度需为3-32位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '登录密码不能为空', trigger: 'blur' },
    { min: 1, max: 32, message: '密码长度需大于4位', trigger: 'blur' },
  ],
}



const handleLogin = async () => {
  if (!loginFormRef.value) return
  const valid = await loginFormRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    await authStore.login({
      account: loginForm.account,
      password: loginForm.password,
    })

    ElMessage.success('登录成功！')

    if (loginForm.remember) {
      localStorage.setItem(
        'rms_login_preference',
        JSON.stringify({ account: loginForm.account, remember: true }),
      )
    } else {
      localStorage.removeItem('rms_login_preference')
    }

        // 登录成功后，初始化权限系统并跳转到合适的页面
    console.log('🔄 登录成功，开始初始化权限系统...')

    // 权限初始化在应用启动时已处理，这里只跳转，让守卫与已注册路由接管
    router.push('/')
  } catch (error) {
    ElMessage.error(error.message || '登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const cache = JSON.parse(localStorage.getItem('rms_login_preference') || '{}')
  if (cache.remember) {
    loginForm.account = cache.account
    loginForm.remember = true
  }
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f0f2f5 v-bind('bgImageUrl') no-repeat center/cover;
}
.login-box {
  width: 400px;
  padding: 30px 40px 40px 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.login-title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 30px;
  color: #333;
}
.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}
.brand-logo {
  width: 32px;
  height: 32px;
  margin-right: 8px;
}
.brand-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-color-primary);
}
</style>
