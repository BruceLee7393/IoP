<template>
  <el-dialog
    title="批量导入订单"
    v-model="dialogVisible"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="import-container">
      <!-- 步骤条 -->
      <el-steps :active="currentStep" finish-status="success" align-center style="margin-bottom: 30px">
        <el-step title="上传文件" />
        <el-step title="导入完成" />
      </el-steps>

      <!-- 步骤1: 上传文件 -->
      <div v-if="currentStep === 0" class="step-content">
        <!-- 导入说明 - 暂时隐藏 -->
        <!-- <el-alert
          title="导入说明"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <template #default>
            <div class="import-tips">
              <p>1. 请下载模板文件，按照模板格式填写订单数据</p>
              <p>2. 订单号必须唯一，机型、料号、序列号范围等字段不能为空</p>
              <p>3. 序列号格式支持：起始--结束（双横线）或换行分隔</p>
              <p>4. 每个订单必须包含至少一个组件，每个组件必须包含至少一个子组件和软件</p>
              <p>5. 如有数据错误，系统将返回带有错误信息的Excel文件，修改后可重新导入</p>
            </div>
          </template>
        </el-alert> -->

        <!-- 下载模板按钮 - 暂时隐藏 -->
        <!-- <div class="download-section">
          <el-button
            type="primary"
            :icon="Download"
            @click="handleDownloadTemplate"
            :loading="downloadingTemplate"
          >
            下载导入模板
          </el-button>
        </div> -->

        <!-- 文件上传 -->
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :before-upload="beforeUpload"
          accept=".xlsx,.xls"
          :limit="1"
          :show-file-list="false"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            点击上传<em>或拖拽文件到此处</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只支持 Excel 文件
            </div>
          </template>
        </el-upload>

        <!-- 已选择文件的大卡片展示 -->
        <div v-if="selectedFile" class="selected-file-card">
          <el-card shadow="hover">
            <div class="file-card-content">
              <div class="file-icon">
                <el-icon :size="48" color="#67C23A">
                  <Document />
                </el-icon>
              </div>
              <div class="file-details">
                <div class="file-name">{{ selectedFile.name }}</div>
                <div class="file-info">
                  <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 步骤2: 导入完成 -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="import-result">
          <el-result
            :icon="importResult.success ? 'success' : 'error'"
            :title="importResult.title"
            :sub-title="importResult.message"
          >
            <template #extra>
              <el-button type="primary" @click="handleClose">完成</el-button>
            </template>
          </el-result>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          v-if="currentStep === 0"
          type="primary"
          @click="handleImport"
          :loading="importing"
          :disabled="!selectedFile"
        >
          {{ importing ? '导入中...' : '开始导入' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, UploadFilled, Document } from '@element-plus/icons-vue'
import { downloadOrderImportTemplate, uploadOrderImportFile } from '@/api/order'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'import-success'])

const dialogVisible = ref(props.modelValue)
const uploadRef = ref(null)
const selectedFile = ref(null)
const currentStep = ref(0)
const uploading = ref(false)
const importing = ref(false)
const downloadingTemplate = ref(false)
const importResult = ref({
  success: false,
  title: '',
  message: ''
})

// 监听 modelValue 变化
watch(() => props.modelValue, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    resetState()
  }
})

// 监听 dialogVisible 变化
watch(dialogVisible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 重置状态
const resetState = () => {
  currentStep.value = 0
  selectedFile.value = null
  uploading.value = false
  importing.value = false
  importResult.value = {
    success: false,
    title: '',
    message: ''
  }
  // 清空上传组件
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 下载模板
const handleDownloadTemplate = async () => {
  try {
    downloadingTemplate.value = true
    await downloadOrderImportTemplate()
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error(error.message || '下载模板失败')
  } finally {
    downloadingTemplate.value = false
  }
}

// 文件选择前验证
const beforeUpload = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                  file.type === 'application/vnd.ms-excel'
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isExcel) {
    ElMessage.error('只支持上传 Excel 文件')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  return true
}

// 文件改变时（自动覆盖之前的文件）
const handleFileChange = (file) => {
  console.log('文件选择:', file)
  // 先清除旧文件
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  // 设置新文件
  selectedFile.value = file.raw
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 执行导入（合并了原来的nextStep和handleImport）
const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要导入的文件')
    return
  }

  try {
    importing.value = true
    console.log('📥 开始导入文件:', selectedFile.value.name)
    
    const result = await uploadOrderImportFile(selectedFile.value)
    console.log('📊 导入结果:', result)

    if (result.type === 'SUCCESS') {
      // 全部导入成功
      importResult.value = {
        success: true,
        title: '导入成功',
        message: `成功导入 ${result.success_count || 0} 条订单`
      }
      ElMessage.success(importResult.value.message)
      
      // 进入完成步骤
      currentStep.value = 1
      
      // 延迟关闭对话框
      setTimeout(() => {
        handleClose()
      }, 2000)
    } else if (result.type === 'PARTIAL_SUCCESS') {
      // 部分成功：导入成功的数据，下载错误文件
      importResult.value = {
        success: true,
        title: '部分导入成功',
        message: `成功导入 ${result.success_count} 条订单，${result.error_count} 条失败。\n错误数据已下载，请修改后重新导入。`
      }
      
      // 自动下载错误文件
      downloadErrorFile(result.blob, result.filename)
      
      ElMessage.warning(`部分导入成功：${result.success_count}条成功，${result.error_count}条失败。错误文件已下载`)
      
      // 进入完成步骤
      currentStep.value = 1
      
      // 延迟关闭对话框
      setTimeout(() => {
        handleClose()
      }, 3000)
    } else {
      // 全部失败，下载错误文件
      importResult.value = {
        success: false,
        title: '本次导入失败',
        message: `返回文件已标注失败原因，请完成修正后再次导入。`
      }
      
      // 自动下载错误文件
      downloadErrorFile(result.blob, result.filename)
      

      
      // 进入完成步骤
      currentStep.value = 1
      
      // 不自动关闭，让用户手动关闭
    }
  } catch (error) {
    console.error('导入失败:', error)
    importResult.value = {
      success: false,
      title: '导入失败',
      message: error.message || '导入失败，请重试'
    }
    ElMessage.error(error.message || '导入失败，请重试')
    currentStep.value = 1
  } finally {
    importing.value = false
    // 无论什么情况都通知父组件刷新表格
    console.log('🔄 通知父组件刷新表格')
    emit('import-success')
  }
}

// 下载错误文件
const downloadErrorFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  resetState()
}
</script>

<style scoped>
.import-container {
  padding: 10px 0;
}

.step-content {
  min-height: 300px;
  padding: 20px 0;
}

.import-tips p {
  margin: 5px 0;
  line-height: 1.6;
  font-size: 14px;
}

.download-section {
  margin: 20px 0;
  text-align: center;
}

.upload-demo {
  margin-top: 20px;
}

.selected-file-card {
  margin-top: 30px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.file-card-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.file-icon {
  flex-shrink: 0;
  margin-right: 20px;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  word-break: break-all;
}

.file-info {
  display: flex;
  align-items: center;
}

.file-size {
  font-size: 14px;
  color: #909399;
}

.el-icon--upload {
  font-size: 67px;
  color: #8c939d;
  margin-bottom: 16px;
}

.el-upload__text {
  font-size: 14px;
  color: #606266;
}

.el-upload__text em {
  color: #409eff;
  font-style: normal;
  margin: 0 4px;
}

.el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 7px;
  line-height: 1.5;
}

.import-result {
  margin-top: 20px;
}

.import-result p {
  margin: 5px 0;
  line-height: 1.6;
}

.dialog-footer {
  text-align: right;
}

/* 上传区域样式优化 */
:deep(.el-upload-dragger) {
  padding: 40px 20px;
}

:deep(.el-upload-list) {
  margin-top: 10px;
}
</style>
