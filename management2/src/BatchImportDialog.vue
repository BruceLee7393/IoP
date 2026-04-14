<template>
  <el-dialog
    :title="`${i18nStore.t('actions.batchImport')}${entityName}`"
    v-model="dialog.visible"
    width="800px"
    v-if="dialog.visible"
    @close="handleClose"
  >
    <div class="import-container">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step :title="i18nStore.t('import.uploadFile')" />
        <el-step :title="i18nStore.t('import.dataPreview')" />
        <el-step :title="i18nStore.t('import.importComplete')" />
      </el-steps>

      <div v-if="currentStep === 0" class="step-content">
        <div class="download-section">
            <el-button type="primary" @click="downloadTemplate" :icon="Download">
              {{ i18nStore.t('import.downloadTemplate') }}
            </el-button>
          </div>


        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :before-upload="beforeUpload"
          accept=".xlsx,.xls,.csv"
          :limit="1"
        >

          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text"><em>{{ i18nStore.t('import.clickUpload') }}</em>{{ i18nStore.t('import.orDragFile') }}</div>
          <template #tip>
            <div class="el-upload__tip">{{ i18nStore.t('import.onlyExcelCsv') }}</div>
          </template>
        </el-upload>


          <div class="template-download">
          <el-alert :title="i18nStore.t('import.importInstructions')" type="info" :closable="false" >
            <template #default>
              <div v-for="tip in importTips" :key="tip">
                <p>{{ tip }}</p>
              </div>
            </template>
          </el-alert>

        </div>
      </div>

      <div v-if="currentStep === 1" class="step-content">
        <div class="preview-info">
          <el-alert
            :title="i18nStore.t('import.parseResult', { totalCount: totalCount, validCount: validCount, errorCount: errorCount })"
            :type="errorCount > 0 ? 'warning' : 'success'"
            :closable="false"
            show-icon
          />
          <div
            v-if="errorCount > 0 && errorFileUrl"
            class="error-file-download"
            style="margin-top: 10px"
          >
            <el-button type="warning" size="small" @click="downloadErrorFile">
              {{ i18nStore.t('import.downloadErrorFile') }}
            </el-button>
            <span style="margin-left: 8px; color: #909399; font-size: 12px">
              {{ i18nStore.t('import.errorFileDescription') }}
            </span>
          </div>
        </div>

        <el-table
          :data="validData"
          border
          stripe
          max-height="400"
          style="width: 100%; margin-top: 20px"
        >
          <el-table-column type="index" :label="i18nStore.t('common.index')" width="60" />
          <el-table-column
            v-for="column in previewColumns"
            :key="column.prop"
            :prop="column.prop"
            :label="column.label"
            :width="column.width"
            :min-width="column.minWidth"
          >
            <template #default="{ row }" v-if="column.formatter">
              <component :is="column.formatter" :row="row" />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-if="currentStep === 2" class="step-content">
        <div class="import-result">
          <el-result
            :icon="importResult.success ? 'success' : 'error'"
            :title="importResult.title"
            :sub-title="importResult.message"
          >
            <template #extra>
              <el-button type="primary" @click="handleClose">{{ i18nStore.t('import.complete') }}</el-button>
            </template>
          </el-result>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">{{ i18nStore.t('common.cancel') }}</el-button>
        <el-button v-if="currentStep > 0 && currentStep < 2" @click="prevStep">{{ i18nStore.t('import.previousStep') }}</el-button>
        <el-button
          v-if="currentStep < 1"
          type="primary"
          @click="nextStep"
          :disabled="currentStep === 0 && !uploadFile"
          :loading="currentStep === 0 && uploading"
        >
          {{ currentStep === 0 && uploading ? i18nStore.t('import.parsing') : i18nStore.t('import.nextStep') }}
        </el-button>
        <el-button
          v-if="currentStep === 1"
          type="primary"
          @click="handleImport"
          :loading="importing"
        >
          {{ validCount === 0 ? i18nStore.t('import.getErrorDetails') : i18nStore.t('import.startImport') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, UploadFilled } from '@element-plus/icons-vue'
import { useI18nStore } from '@/stores/i18n'

const i18nStore = useI18nStore()

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  entityName: { type: String, required: true },
  importTips: { type: Array, required: true },
  templateData: { type: Array, default: () => [] },
  previewColumns: { type: Array, required: true },
  uploadApi: { type: Function, required: true },
  importApi: { type: Function, required: true },
  downloadTemplateApi: { type: Function, default: null },
})
const emit = defineEmits(['update:modelValue', 'importSuccess'])

const uploadRef = ref(null)
const currentStep = ref(0)
const uploadFile = ref(null)
const previewData = ref([])
const importing = ref(false)
const uploading = ref(false)
const uploadResult = ref(null)
const errorFileUrl = ref(null)

const dialog = reactive({ visible: props.modelValue })
const importResult = reactive({ success: false, title: '', message: '' })

const validData = computed(() => uploadResult.value?.valid_records || uploadResult.value?.validData || [])
const totalCount = computed(() => uploadResult.value?.total_records || uploadResult.value?.totalCount || 0)
const validCount = computed(() => uploadResult.value?.valid_count || uploadResult.value?.validCount || 0)
const errorCount = computed(() => uploadResult.value?.invalid_count || uploadResult.value?.errorCount || 0)

watch(() => props.modelValue, (newValue) => {
  dialog.visible = newValue
  if (newValue) {
    currentStep.value = 0
    uploadFile.value = null
    previewData.value = []
    importing.value = false
    uploading.value = false
    uploadResult.value = null
    errorFileUrl.value = null
    importResult.success = false
    importResult.title = ''
    importResult.message = ''
  }
}, { immediate: true })

const downloadTemplate = async () => {
  try {
    if (props.downloadTemplateApi) {
      await props.downloadTemplateApi()
    } else {
      const XLSX = await import('xlsx')
      const ws = XLSX.utils.json_to_sheet(props.templateData)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, `${props.entityName}${i18nStore.t('import.template')}`)
      XLSX.writeFile(wb, `${props.entityName}${i18nStore.t('import.template')}.xlsx`)
    }
    ElMessage.success(i18nStore.t('messages.templateDownloadSuccess'))
  } catch (error) {
    ElMessage.error(i18nStore.t('messages.templateDownloadFailed'))
  }
}

const beforeUpload = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || file.type === 'application/vnd.ms-excel' || file.type === 'text/csv'
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isExcel) ElMessage.error(i18nStore.t('messages.onlyExcelCsvAllowed'))
  if (!isLt10M) ElMessage.error(i18nStore.t('messages.fileSizeLimit'))
  return isExcel && isLt10M
}

const handleFileChange = (file) => {
  uploadFile.value = file.raw
}

// 【修改点4】调整 nextStep 的逻辑
const nextStep = async () => {
  // 当在第一步（currentStep === 0）并且已经选择了文件时，执行上传和解析
  if (currentStep.value === 0 && uploadFile.value) {
    try {
      uploading.value = true
      const result = await props.uploadApi(uploadFile.value)
      uploadResult.value = result
      previewData.value = result.valid_records || result.validData || []
      if (result.errorFileUrl) errorFileUrl.value = result.errorFileUrl
      currentStep.value++ // 进入预览步骤
    } catch (error) {
      ElMessage.error(i18nStore.t('messages.fileUploadParseFailed', { error: error.message || i18nStore.t('messages.unknownError') }))
    } finally {
      uploading.value = false
    }
  } else {
    // 其他情况（例如从下载模板到上传文件），直接进入下一步
    currentStep.value++
  }
}

const prevStep = () => { currentStep.value-- }

const handleImport = async () => {
  importing.value = true
  try {
    const importData = {
      import_token: uploadResult.value.import_token,
      valid_records: validData.value,
    }
    const result = await props.importApi(importData)

    if (result.type === 'PARTIAL_SUCCESS_WITH_ERRORS' && result.hasErrorFile) {
      const { downloadFile } = await import('@/utils/apiUtils')
      downloadFile(result.blob, result.filename, {}, i18nStore.t('import.errorInfo'))
      if (validCount.value > 0) {
        importResult.success = true
        importResult.title = i18nStore.t('messages.importPartialSuccess')
        importResult.message = i18nStore.t('messages.importPartialSuccessMessage', {
          validCount: validCount.value,
          errorCount: errorCount.value
        })
        ElMessage.warning(importResult.message)
      } else {
        importResult.success = false
        importResult.title = i18nStore.t('messages.importFailed')
        importResult.message = i18nStore.t('messages.importAllFailedMessage', { totalCount: totalCount.value })
        ElMessage.error(importResult.message)
      }
    } else {
      importResult.success = true
      importResult.title = i18nStore.t('messages.importSuccess')
      const successCount = result.success_count || validCount.value
      importResult.message = i18nStore.t('messages.importSuccessMessage', {
        count: successCount,
        entity: props.entityName
      })
      ElMessage.success(importResult.message)
    }
    emit('importSuccess')
    currentStep.value = 2 // 成功后进入结果页
  } catch (error) {
    importResult.success = false
    importResult.title = i18nStore.t('messages.importFailed')
    importResult.message = error.message || i18nStore.t('messages.importUnknownError')
    ElMessage.error(importResult.message)
    currentStep.value = 2 // 失败后也进入结果页
  } finally {
    importing.value = false
  }
}

const downloadErrorFile = () => {
  if (errorFileUrl.value) {
    const link = document.createElement('a')
    link.href = errorFileUrl.value
    link.download = `${props.entityName}${i18nStore.t('import.errorData')}.xlsx`
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success(i18nStore.t('messages.errorFileDownloadSuccess'))
  } else {
    ElMessage.error(i18nStore.t('messages.errorFileNotExists'))
  }
}

const handleClose = () => {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.import-container {
  padding: 20px 0;
}

.step-content {
  margin-top: 30px;
  min-height: 300px;
}

/* 【修改点5】为合并后的第一步添加一些间距 */
.template-download {
  text-align: left;
  margin-bottom: 24px; /* 在下载模板和上传区域之间增加一些间距 */
  margin-top: 20px;
}

.download-section {
  margin-top: 20px;
}

.upload-demo {
  margin-top: 20px;
}

.preview-info {
  margin-bottom: 20px;
}

.import-result {
  text-align: center;
}

.dialog-footer {
  text-align: right;
}
</style>
