<template>
  <div class="order-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="handleGoBack">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
      </div>
      <div class="header-right">
        <el-button
          type="primary"
          @click="openEditDialog"
        >
          <el-icon><Edit /></el-icon>
          编辑订单
        </el-button>
      </div>
    </div>

    <!-- 订单基本信息 -->
    <el-card class="info-card" shadow="never">
      <template #header>
        <span class="card-title">订单基本信息</span>
      </template>
      
      <div v-if="orderInfo" class="order-info">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="订单号">
            {{ orderInfo.order_number }}
          </el-descriptions-item>
          <el-descriptions-item label="机型">
            {{ orderInfo.model }}
          </el-descriptions-item>
          <el-descriptions-item label="料号">
            {{ orderInfo.part_number }}
          </el-descriptions-item>
          <el-descriptions-item label="序列号范围">
            {{ getSerialNumberRange(orderInfo) }}
          </el-descriptions-item>
          <el-descriptions-item label="生产日期">
            {{ formatDateTime(orderInfo.order_created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(orderInfo.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="备注">
            {{ orderInfo.remark || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- 组件层级信息 -->
    <el-card class="components-card" shadow="never" v-loading="loading">
      <template #header>
        <span class="card-title">组件层级信息</span>
      </template>

      <div v-if="flattenedData.length > 0" class="components-table-container">
        <table class="hierarchy-table">
          <thead>
            <tr>
              <th>组件名称</th>
              <th>组件料号</th>
              <th>名称</th>
              <th>子组件料号</th>
              <th>规格型号</th>
              <th>软件名称</th>
              <th>软件版本号</th>
              <th>软件附件</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in flattenedData" :key="index">
              <!-- 组件名称列 -->
              <td
                v-if="item.showComponent"
                :rowspan="item.componentRowspan"
                class="component-cell merged-cell"
              >
                {{ item.component_name }}
              </td>

              <!-- 组件料号列 -->
              <td
                v-if="item.showComponent"
                :rowspan="item.componentRowspan"
                class="component-cell merged-cell"
              >
                {{ item.component_part_number }}
              </td>

              <!-- 子组件名称列 -->
              <td
                v-if="item.showSubComponent"
                :rowspan="item.subComponentRowspan"
                class="sub-component-cell merged-cell"
              >
                {{ item.sub_component_name }}
              </td>

              <!-- 子组件料号列 -->
              <td
                v-if="item.showSubComponent"
                :rowspan="item.subComponentRowspan"
                class="sub-component-cell merged-cell"
              >
                {{ item.sub_component_part_number }}
              </td>

              <!-- 规格型号列 -->
              <td
                v-if="item.showSubComponent"
                :rowspan="item.subComponentRowspan"
                class="sub-component-cell merged-cell"
              >
                {{ item.specification || '-' }}
              </td>

              <!-- 软件名称列 -->
              <td class="software-cell">
                {{ item.software_name || '-' }}
              </td>

              <!-- 软件版本列 -->
              <td class="software-cell">
                {{ item.software_version || '-' }}
              </td>

              <!-- 软件附件列 -->
              <td class="software-cell attachment-cell">
                <div v-if="item.software_id" class="software-attachment">
                  <FileUpload
                    :current-attachment="item.attachment"
                    :upload-function="(file) => handleUploadSoftwareAttachment(item.software_id, file)"
                    :download-function="() => handleDownloadSoftwareAttachment(item.software_id, item.attachment)"
                    @upload-success="handleSoftwareAttachmentUploadSuccess(item, $event)"
                  />
                </div>
                <span v-else>-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-else class="empty-components">
        <el-empty description="该订单暂无组件信息" />
      </div>
    </el-card>

    <!-- 主从结构编辑器弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑订单"
      width="1200px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      destroy-on-close
    >
      <OrderMasterDetailEditor
        :model-value="editDialogVisible"
        :is-edit="true"
        :initial-data="orderInfo"
        @update:model-value="editDialogVisible = $event"
        @submit="handleEditSubmit"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ArrowLeft, Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useOrderDetailManagement } from '@/composables/cfg/useOrderDetailManagement'
import OrderMasterDetailEditor from '@/components/order/OrderMasterDetailEditor.vue'
import FileUpload from '@/components/business/FileUpload.vue'
import { useOrderManagement } from '@/composables/cfg/useOrderManagement'
import { uploadSoftwareAttachment, downloadSoftwareAttachment } from '@/api/order'

// 使用订单详情管理配置
const {
  loading,
  orderInfo,
  flattenedData,
  fetchOrderDetail,
  handleGoBack,
  formatDateTime,
} = useOrderDetailManagement()

// 编辑对话框状态
const editDialogVisible = ref(false)

// 获取订单管理API
const { api } = useOrderManagement()

// 打开编辑对话框
const openEditDialog = () => {
  editDialogVisible.value = true
}

// 处理编辑提交
const handleEditSubmit = async (orderData) => {
  try {
    // 调用更新API
    await api.update(orderInfo.value.id, orderData)

    ElMessage.success('订单更新成功')
    editDialogVisible.value = false

    // 重新获取订单详情
    await fetchOrderDetail()
  } catch (error) {
    console.error('更新订单失败:', error)
    ElMessage.error('更新订单失败')
  }
}

// 获取序列号范围显示
const getSerialNumberRange = (order) => {
  if (order && order.serial_number_start && order.serial_number_end) {
    return `${order.serial_number_start} - ${order.serial_number_end}`
  }
  return '-'
}

// 处理软件附件上传
const handleUploadSoftwareAttachment = async (softwareId, file) => {
  try {
    const result = await uploadSoftwareAttachment(softwareId, file)
    console.log('软件附件上传成功:', result)
    return result
  } catch (error) {
    console.error('软件附件上传失败:', error)
    throw error
  }
}

// 处理软件附件下载
const handleDownloadSoftwareAttachment = async (softwareId, originalFilename) => {
  try {
    const result = await downloadSoftwareAttachment(softwareId, originalFilename)
    console.log('软件附件下载成功:', result)
    return result
  } catch (error) {
    console.error('软件附件下载失败:', error)
    throw error
  }
}

// 处理软件附件上传成功
const handleSoftwareAttachmentUploadSuccess = (item, result) => {
  console.log('软件附件上传成功回调:', { item, result })

  // 更新软件项的附件信息
  if (result) {
    // 优先使用原始文件名，避免显示服务器存储的ID文件名
    const filename = result.original_filename || result.filename || result.file_name || result.attachment || result.data?.filename
    if (filename) {
      // 直接更新当前行的附件信息
      item.attachment = filename
      console.log('更新软件附件信息:', filename)

      // 同时更新原始数据中的软件附件信息
      if (orderInfo.value && orderInfo.value.components && item.software_id) {
        for (const component of orderInfo.value.components) {
          if (component.sub_components) {
            for (const subComponent of component.sub_components) {
              if (subComponent.softwares) {
                for (const software of subComponent.softwares) {
                  if (software.id === item.software_id) {
                    // 同时更新两个可能的字段名
                    software.attachment = filename
                    software.appendix = filename
                    console.log('同步更新原始数据中的软件附件:', filename)
                    break
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  // 不需要重新获取数据，因为我们已经直接更新了
  console.log('软件附件上传完成，UI已更新')
}

// 初始化
onMounted(() => {
  fetchOrderDetail()
})
</script>

<style scoped>
.order-detail-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.info-card {
  margin-bottom: 20px;
}

.card-title {
  font-weight: bold;
  font-size: 16px;
}

.components-table-container {
  overflow-x: auto;
}

.hierarchy-table {
  width: 100%;
  border-collapse: collapse;
  border: 2px solid #000;
  font-size: 14px;
  background-color: #fff;
}

.hierarchy-table th,
.hierarchy-table td {
  border: 1px solid #000;
  padding: 8px 12px;
  text-align: center;
  vertical-align: middle;
  background-color: #fff;
  position: relative;
}

.hierarchy-table th {
  background-color: #f0f0f0;
  font-weight: bold;
  color: #000;
  font-size: 13px;
  border: 1px solid #000;
}

/* 合并单元格样式 */
.merged-cell {
  background-color: #fff;
  font-weight: bold;
  border: 1px solid #000;
}

.component-cell {
  background-color: #fff;
  color: #000;
  font-weight: bold;
  border: 1px solid #000;
}

.sub-component-cell {
  background-color: #fff;
  color: #000;
  font-weight: bold;
  border: 1px solid #000;
}

.software-cell {
  background-color: #fff;
  color: #000;
  border: 1px solid #000;
}

.empty-components {
  text-align: center;
  padding: 40px 0;
}

.attachment-cell {
  padding: 4px;
  min-width: 200px;
}

.software-attachment {
  width: 100%;
}

.attachment-cell :deep(.file-upload-container) {
  font-size: 11px;
}

.attachment-cell :deep(.current-attachment) {
  margin-bottom: 0;
}

.attachment-cell :deep(.attachment-info) {
  padding: 4px 6px;
  font-size: 11px;
}

.attachment-cell :deep(.upload-area) {
  margin-bottom: 0;
}

.attachment-cell :deep(.upload-content) {
  padding: 15px 8px;
}

.attachment-cell :deep(.upload-icon) {
  font-size: 20px;
  margin-bottom: 6px;
}

.attachment-cell :deep(.upload-text p) {
  font-size: 10px;
  margin: 1px 0;
}

.attachment-cell :deep(.selected-file) {
  margin-bottom: 0;
}

.attachment-cell :deep(.file-info) {
  padding: 4px 6px;
  font-size: 10px;
}

.attachment-cell :deep(.file-actions .el-button) {
  font-size: 10px;
  padding: 2px 6px;
}

.attachment-cell :deep(.replace-warning) {
  margin-top: 4px;
}

.attachment-cell :deep(.upload-progress) {
  margin-bottom: 4px;
}
</style>
