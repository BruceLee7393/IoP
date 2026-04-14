<template>
  <div v-loading="loading" class="personal-center">

      <el-row :gutter="12">
        <!-- 左侧头像信息区域移除，仅保留右侧内容，全宽展示 -->
        <el-col :span="24">
        <el-card>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="个人资料" name="profile">
              <el-form :model="profileForm" label-width="100px">
                <el-form-item label="账号">
                  <el-input v-model="profileForm.account" disabled />
                 </el-form-item>
                 <el-form-item label="姓名">
                   <el-input v-model="profileForm.full_name" />
                 </el-form-item>
                 <el-form-item label="联系方式">
                   <el-input v-model="profileForm.contact_info" />
                 </el-form-item>
                <el-form-item label="性别">
                  <el-select v-model="profileForm.gender" placeholder="请选择性别">
                    <el-option label="男" value="man" />
                    <el-option label="女" value="woman" />
                    <el-option label="其他" value="others" />
                    <el-option label="不愿透露性别" value="none" />
                  </el-select>
                </el-form-item>
                 <el-form-item label="地址">
                   <el-input v-model="profileForm.address" type="textarea" />
                 </el-form-item>
                <el-form-item label="所属角色">
                  <el-input :value="userInfo.role?.role_name || '无角色'" disabled />
                 </el-form-item>
                

                <el-form-item label="创建时间">
                  <el-input :value="formatDateTime(userInfo.created_at)" disabled />
                 </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="saveProfile">保存</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="修改密码" name="password">
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="80px"
              >
                <el-form-item label="新密码" prop="password">
                  <el-input v-model="passwordForm.password" type="password" show-password />
                </el-form-item>
                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="changePassword">修改密码</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCurrentUserInfo, updateCurrentUserPassword, updateCurrentUserProfile } from '@/api/user'
import { useAuthStore } from '@/stores/auth'
import { setUserInfo } from '@/utils/token'

const activeTab = ref('profile')
const authStore = useAuthStore()
const loading = ref(false)

// 用户信息
const userInfo = ref({})

// 个人资料表单
const profileForm = reactive({
  account: '',
  full_name: '',
  contact_info: '',
  gender: '',
  address: '',
})

// 格式化时间
const formatDateTime = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  if (isNaN(date.getTime())) return ''

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${year}/${month}/${day} ${hours}:${minutes}`
}

// 获取用户信息
const fetchUserInfo = async () => {
  loading.value = true
  try {
    const response = await getCurrentUserInfo()
    console.log('🔍 获取用户信息原始响应:', response)

    // HTTP拦截器已经处理了响应格式，直接使用response.data
    const userData = response.data || response
    console.log('🔍 解析后的用户数据:', userData)

    if (userData && (userData.id || userData.account)) {
      userInfo.value = userData

      // 填充表单数据
      profileForm.account = userData.account || ''
      profileForm.full_name = userData.full_name || ''
      profileForm.contact_info = userData.contact_info || ''
      // 性别枚举兼容历史值
      const gender = userData.gender || ''
      profileForm.gender = gender === 'secret' ? 'none' : (gender === 'other' ? 'others' : gender)
      profileForm.address = userData.address || ''

      console.log('✅ 用户信息加载成功:', userInfo.value)
    } else {
      console.error('❌ 用户数据格式错误:', userData)
      ElMessage.error('用户数据格式错误')
    }
  } catch (error) {
    console.error('❌ 获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败: ' + (error.message || '网络错误'))
  } finally {
    loading.value = false
  }
}

const passwordFormRef = ref(null)
const passwordForm = reactive({
  password: '',
  confirmPassword: '',
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    if (passwordForm.confirmPassword !== '') {
      passwordFormRef.value.validateField('confirmPassword')
    }
    callback()
  }
}

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.password) {
    callback(new Error('两次输入的密码不一致!'))
  } else {
    callback()
  }
}

const passwordRules = reactive({
  password: [{ required: true, validator: validatePass, trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validatePass2, trigger: 'blur' }],
})

const saveProfile = async () => {
  try {
    const payload = {
      full_name: profileForm.full_name?.trim() || '',
      contact_info: profileForm.contact_info?.trim() || '',
      address: profileForm.address?.trim() || '',
      gender: profileForm.gender || '', // woman | man | none | others
    }

    await updateCurrentUserProfile(payload)

    // 保存成功后刷新当前用户信息并同步到 authStore 与 localStorage
    const res = await getCurrentUserInfo()
    const latest = res.data || res
    userInfo.value = latest || {}

    // 同步 store 和本地缓存
    authStore.user = userInfo.value
    setUserInfo(userInfo.value)

    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败：' + (error.message || '请稍后重试'))
  }
}

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})

const changePassword = async () => {
  if (!passwordFormRef.value) return

  try {
    const valid = await passwordFormRef.value.validate()
    if (valid) {
      loading.value = true

            // 调用修改密码API
      await updateCurrentUserPassword({
        password: passwordForm.password
      })

      ElMessage.success('密码修改成功！')

      // 重置表单
      Object.assign(passwordForm, {
        password: '',
        confirmPassword: '',
      })
    }
  } catch (error) {
    console.error('❌ 修改密码失败:', error)
    ElMessage.error('修改密码失败: ' + (error.message || '网络错误'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.personal-center {
  padding: 20px;
}

.user-profile {
  text-align: center;
  padding: 20px;
}

.user-name {
  font-size: 20px;
  font-weight: bold;
  margin-top: 10px;
  color: #303133;
}

.user-role {
  color: #606266;
  margin-top: 5px;
  font-size: 14px;
}



.user-status {
  margin-top: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: inline-block;
}

.user-status.enabled {
  background-color: #f0f9ff;
  color: #67c23a;
}

.user-status.disabled {
  background-color: #fef0f0;
  color: #f56c6c;
}
</style>
