<template>
  <div class="file-upload-container">
    <div v-if="currentAttachment && !isUploading" class="current-attachment">
      <div class="attachment-actions">
        <div class="file-info">
          <el-icon class="file-icon"><Document /></el-icon>
          <span class="filename" @click="handleDownload">{{ currentAttachment }}</span>
        </div>
        <el-button type="primary" size="small" @click="triggerFileSelect" :disabled="disabled">
          更新
        </el-button>
      </div>
    </div>

    <div v-if="!currentAttachment && !isUploading" class="upload-button-area">
      <el-button type="primary" size="small" @click="triggerFileSelect" :disabled="disabled">
        <el-icon><UploadFilled /></el-icon>
        上传附件
      </el-button>
    </div>

    <input
      ref="fileInputRef"
      type="file"
      :accept="acceptedTypes"
      style="display: none"
      @change="handleFileInputChange"
    />

    <div v-if="isUploading" class="upload-progress">
      <div class="progress-info">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>正在上传 {{ uploadingFileName }}...</span>
      </div>
      <el-progress :percentage="uploadProgress" :show-text="false" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, UploadFilled, Loading } from '@element-plus/icons-vue'
import { formatFileSize, validateFileType } from '@/utils/fileUtils'

const props = defineProps({
  // 当前附件文件名
  currentAttachment: {
    type: String,
    default: ''
  },
  // 上传函数
  uploadFunction: {
    type: Function,
    required: true
  },
  // 下载函数
  downloadFunction: {
    type: Function,
    required: true
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['upload-success', 'upload-error'])

// 允许的文件扩展名
const allowedExtensions = ['zip', 'rar', '7z', 'tar', 'gz']

// 文件大小限制（128MB）
const MAX_FILE_SIZE = 128 * 1024 * 1024

// 响应式数据
const fileInputRef = ref(null)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadingFileName = ref('')

// 计算属性
const acceptedTypes = computed(() => {
  return allowedExtensions.map(ext => `.${ext}`).join(',')
})

// 方法
const triggerFileSelect = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

const validateFile = (file) => {
  // 验证文件类型
  const isValidType = validateFileType(file, allowedExtensions)
  if (!isValidType) {
    ElMessage.error(`仅支持 ${allowedExtensions.join(', ')} 格式的压缩文件`)
    return false
  }

  // 验证文件大小
  if (file.size > MAX_FILE_SIZE) {
    ElMessage.error('文件大小超过128MB限制')
    return false
  }

  return true
}

const handleFileInputChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件
  if (!validateFile(file)) {
    // 清空文件输入框
    event.target.value = ''
    return
  }

  // 如果已有附件，显示确认对话框
  if (props.currentAttachment) {
    try {
      await ElMessageBox.confirm(
        '上传新文件将覆盖现有附件，是否继续？',
        '确认覆盖',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
    } catch {
      // 用户取消，清空文件输入框
      event.target.value = ''
      return
    }
  }

  // 直接上传文件
  await uploadFile(file)

  // 清空文件输入框
  event.target.value = ''
}

const uploadFile = async (file) => {
  try {
    isUploading.value = true
    uploadProgress.value = 0
    uploadingFileName.value = file.name

    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 100)

    // 调用上传函数
    const result = await props.uploadFunction(file)

    clearInterval(progressInterval)
    uploadProgress.value = 100

    // 延迟一下显示完成状态
    setTimeout(() => {
      ElMessage.success('文件上传成功')
      emit('upload-success', result)

      // 重置状态
      isUploading.value = false
      uploadProgress.value = 0
      uploadingFileName.value = ''
    }, 500)

  } catch (error) {
    isUploading.value = false
    uploadProgress.value = 0
    uploadingFileName.value = ''

    console.error('文件上传失败:', error)

    // 更详细的错误处理
    let errorMessage = '文件上传失败'
    if (error.message) {
      if (error.message.includes('413')) {
        errorMessage = '文件过大，请选择较小的文件'
      } else if (error.message.includes('415')) {
        errorMessage = '不支持的文件格式'
      } else if (error.message.includes('网络')) {
        errorMessage = '网络连接失败，请检查网络后重试'
      } else {
        errorMessage = `文件上传失败：${error.message}`
      }
    }

    ElMessage.error(errorMessage)
    emit('upload-error', error)
  }
}

const handleDownload = async () => {
  if (!props.currentAttachment) {
    ElMessage.error('没有可下载的附件')
    return
  }

  try {
    await props.downloadFunction()
    ElMessage.success('文件下载成功')
  } catch (error) {
    console.error('文件下载失败:', error)

    // 更详细的错误处理
    let errorMessage = '文件下载失败'
    if (error.message) {
      if (error.message.includes('404')) {
        errorMessage = '文件不存在或已被删除'
      } else if (error.message.includes('403')) {
        errorMessage = '没有权限下载此文件'
      } else if (error.message.includes('网络')) {
        errorMessage = '网络连接失败，请检查网络后重试'
      } else {
        errorMessage = `文件下载失败：${error.message}`
      }
    }

    ElMessage.error(errorMessage)
  }
}
</script>

<style scoped>
.file-upload-container {
  width: 100%;
}

.current-attachment {
  margin-bottom: 16px;
}

.attachment-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  /* --- 新增关键样式 --- */
  flex: 1; /* 1. 让它占据所有可用的剩余空间 */
  min-width: 0; /* 2. 允许该元素收缩到比其内容还小，这是让省略号生效的关键！ */
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
}

.file-icon {
  font-size: 18px;
  color: #409eff;
  /* --- 新增样式 --- */
  flex-shrink: 0; /* 防止图标在极端情况下被压缩 */
}

.filename {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
  font-weight: 500;
  /* --- 修改和新增关键样式 --- */
  /* flex: 1; */ /* 移除或注释掉这一行 */
  white-space: nowrap; /* 1. 强制文本不换行 */
  overflow: hidden; /* 2. 隐藏超出的部分 */
  text-overflow: ellipsis; /* 3. 将隐藏的部分显示为省略号 */
}

.filename:hover {
  color: #66b1ff;
}

.upload-button-area {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
}

.upload-progress {
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.loading-icon {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>