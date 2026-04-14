<template>
  <div class="order-management-container management-container">
    <CrudTable
      ref="crudRef"
      :api="api"
      entity-name="订单"
      :columns="tableColumns"
      :query-fields="queryFields"
      :form-component="OrderFormDialog"
      :form-props="formProps"
      :initial-query-params="initialQueryParams"
      :permissions="permissions"
      :header-action-config="headerActionConfig"
      :row-action-config="rowActionConfig"
      @action="handleAction"
    >
      <!-- 序列号范围列模板 -->
      <template #cell-serial_range="{ row }">
        <span>{{ row.serial_number_start }} ~ {{ row.serial_number_end }}</span>
      </template>

      <!-- 组件数量列模板 -->
      <template #cell-component_count="{ row }">
        <el-tag size="small" type="info">
          {{ (row.component_count || 0) }}个
        </el-tag>
      </template>

      <!-- 订单号列模板（可点击查看详情） -->
      <template #cell-order_number="{ row }">
        <span
          class="order-number-link"
          @click="handleViewDetail(row)"
        >
          {{ row.order_number }}
        </span>
      </template>

      <!-- 附件列模板 -->
      <template #cell-appendix="{ row }">
        <div class="attachment-cell">
          <FileUpload
            :current-attachment="row.appendix"
            :upload-function="(file) => handleUploadOrderAttachment(row.id, file)"
            :download-function="() => handleDownloadOrderAttachment(row.id, row.appendix)"
            @upload-success="handleAttachmentUploadSuccess(row, $event)"
          />
        </div>
      </template>

    </CrudTable>

    <!-- 批量导入对话框 -->
    <OrderImportDialog
      v-model="showImportDialog"
      @import-success="handleImportSuccess"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import CrudTable from '@/components/business/CrudTable.vue'
import OrderFormDialog from '@/components/dialog/OrderFormDialog.vue'
import OrderImportDialog from '@/components/dialog/OrderImportDialog.vue'
import FileUpload from '@/components/business/FileUpload.vue'
import { useOrderManagement } from '@/composables/cfg/useOrderManagement'
import { uploadOrderAttachment, downloadOrderAttachment } from '@/api/order'

// 使用订单管理配置
const {
  initialQueryParams,
  queryFields,
  tableColumns,
  permissions,
  headerActionConfig,
  rowActionConfig,
  api,
  initializeData,
  handleCustomAction,
  handleViewDetail,
} = useOrderManagement()

const crudRef = ref(null)
const router = useRouter()
const showImportDialog = ref(false)

// 表单属性配置
const formProps = ref({
  editBasicOnly: false,
  useMasterDetail: false
})

// 初始化数据
onMounted(async () => {
  await initializeData()

  // 检查是否有编辑参数
  const route = router.currentRoute.value
  if (route.query.action === 'edit' && route.query.id) {
    // 延迟执行，确保组件已完全加载
    setTimeout(() => {
      handleEditFromDetail(route.query.id)
    }, 500)
  }
})

// 处理从详情页面跳转过来的编辑操作
const handleEditFromDetail = async (orderId) => {
  try {
    // 获取订单详情数据
    const response = await api.getDetail(orderId)
    const orderData = response.data || response

    // 打开主从结构编辑对话框（详情页编辑应该支持完整编辑）
    if (crudRef.value) {
      // 设置为主从结构模式
      formProps.value = {
        editBasicOnly: false,
        useMasterDetail: true
      }

      // 打开编辑对话框
      crudRef.value.openEditDialog(orderData)
    }

    // 清除URL参数
    router.replace({ path: '/order' })
  } catch (error) {
    console.error('获取订单数据失败:', error)
    ElMessage.error('获取订单数据失败')
  }
}



// 处理所有操作
const handleAction = ({ type, action, data }) => {
  console.log('OrderView handleAction:', { type, action, data })

  // 处理批量导入操作
  if (type === 'header' && action === 'batchImport') {
    showImportDialog.value = true
    return
  }

  if (type === 'header' && action === 'add') {
    // 对于新增操作，使用主从结构模式
    console.log('设置主从结构模式')
    formProps.value = {
      editBasicOnly: false,
      useMasterDetail: true
    }

    console.log('打开添加对话框，formProps:', formProps.value)
    // 直接打开对话框，不需要延迟
    if (crudRef.value && crudRef.value.openAddDialog) {
      crudRef.value.openAddDialog({})
    }

    // 不调用其他处理，直接返回
    return
  } else if (type === 'row' && action === 'edit') {
    // 对于行操作的编辑，使用基本信息编辑模式
    formProps.value = {
      editBasicOnly: true,
      useMasterDetail: false
    }
  }

  // 调用原有的自定义操作处理
  return handleCustomAction({ type, action, data })
}

// 处理导入成功
const handleImportSuccess = () => {
  console.log('导入成功，刷新表格数据')
  // 刷新表格数据
  if (crudRef.value && crudRef.value.refresh) {
    crudRef.value.refresh()
  }
}

// 处理订单附件上传
const handleUploadOrderAttachment = async (orderId, file) => {
  try {
    const result = await uploadOrderAttachment(orderId, file)
    console.log('订单附件上传成功:', result)
    return result
  } catch (error) {
    console.error('订单附件上传失败:', error)
    throw error
  }
}

// 处理订单附件下载
const handleDownloadOrderAttachment = async (orderId, originalFilename) => {
  try {
    const result = await downloadOrderAttachment(orderId, originalFilename)
    console.log('订单附件下载成功:', result)
    return result
  } catch (error) {
    console.error('订单附件下载失败:', error)
    throw error
  }
}

// 处理附件上传成功
const handleAttachmentUploadSuccess = (row, result) => {
  console.log('订单附件上传成功回调:', { row, result })

  // 更新行数据中的附件信息
  if (result) {
    // 优先使用原始文件名，避免显示服务器存储的ID文件名
    const filename = result.original_filename || result.filename || result.file_name || result.attachment || result.data?.filename
    if (filename) {
      row.appendix = filename
      console.log('更新订单附件信息:', filename)
    }
  }

  // 刷新表格数据
  setTimeout(() => {
    if (crudRef.value && crudRef.value.refresh) {
      crudRef.value.refresh()
    }
  }, 500)
}
</script>

<style scoped>
.order-management-container {
  padding: 20px;
}

.order-number-link {
  color: var(--el-color-primary);
  cursor: pointer;
  transition: color 0.3s;
}

.order-number-link:hover {
  color: var(--el-color-primary-light-3);
}

.attachment-cell {
  padding: 4px;
}

.attachment-cell :deep(.file-upload-container) {
  font-size: 12px;
}

.attachment-cell :deep(.current-attachment) {
  margin-bottom: 0;
}

.attachment-cell :deep(.attachment-info) {
  padding: 6px 8px;
  font-size: 12px;
}

.attachment-cell :deep(.upload-area) {
  margin-bottom: 0;
}

.attachment-cell :deep(.upload-content) {
  padding: 20px 10px;
}

.attachment-cell :deep(.upload-icon) {
  font-size: 24px;
  margin-bottom: 8px;
}

.attachment-cell :deep(.upload-text p) {
  font-size: 11px;
  margin: 2px 0;
}

.attachment-cell :deep(.selected-file) {
  margin-bottom: 0;
}

.attachment-cell :deep(.file-info) {
  padding: 6px 8px;
  font-size: 11px;
}

.attachment-cell :deep(.file-actions .el-button) {
  font-size: 11px;
  padding: 4px 8px;
}
</style>
