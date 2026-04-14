<template>
  <BaseDialog
    v-if="!useMasterDetail"
    :model-value="modelValue"
    :title="dialogTitle"
    :width="900"
    :loading="loading"
    :readonly="mode === 'view'"
    @update:model-value="$emit('update:modelValue', $event)"
    @confirm="handleConfirm"
    @cancel="handleCancel"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      :disabled="mode === 'view'"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <!-- 模板操作按钮 -->
        <div v-if="mode === 'create'" class="template-actions">
          <el-button
            type="success"
            size="small"
            @click="loadTemplate"
            :icon="Plus"
          >
            加载模板
          </el-button>
          <el-button
            type="warning"
            size="small"
            @click="clearAllData"
            :icon="Delete"
          >
            清除所有信息
          </el-button>
        </div>

        <div class="form-content">
          <el-row :gutter="20">
  <el-col :span="24">
    <el-form-item label="订单号" prop="order_number">
      <el-input v-model="formData.order_number" placeholder="请输入订单号" />
    </el-form-item>
  </el-col>
</el-row>
<el-row :gutter="20">
  <el-col :span="24">
    <el-form-item label="机型" prop="model">
      <el-input v-model="formData.model" placeholder="请输入机型" />
    </el-form-item>
  </el-col>
</el-row>

          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="料号" prop="part_number">
                <el-input v-model="formData.part_number" placeholder="请输入料号" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="序列号范围" prop="serial_number_range">
                <el-input
                  v-model="formData.serial_number_range"
                  placeholder="请输入序列号范围，如：SNX1001-SNX1100 或 SNX1001~SNX1100"
                  @input="handleSerialNumberRangeChange"
                >

                </el-input>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="生产日期" prop="order_created_at">
                <el-date-picker
                  v-model="formData.order_created_at"
                  type="datetime"
                  placeholder="请选择生产日期"
                  format="YYYY-MM-DD HH:mm:ss"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="备注" prop="remark">
                <el-input
                  v-model="formData.remark"
                  type="textarea"
                  placeholder="请输入备注信息（可选）"
                  :rows="3"
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 组件信息 -->
      <div v-if="showComponentSection || mode === 'view'" class="form-section">
        <div class="section-header">
          <h3 class="section-title">组件信息</h3>
          <el-button
            v-if="showComponentSection"
            type="primary"
            size="small"
            @click="addComponent"
            class="add-btn"
          >
            <el-icon><Plus /></el-icon>
            添加组件
          </el-button>
        </div>

        <div v-if="formData.components && formData.components.length > 0" class="components-container">
          <div
            v-for="(component, componentIndex) in formData.components"
            :key="componentIndex"
            class="component-item"
          >
            <!-- 组件标题栏 -->
            <div class="item-header component-header">
              <div class="header-left">
                <span class="item-number">{{ componentIndex + 1 }}</span>
                <span class="item-title">组件</span>
              </div>
              <el-button
                v-if="mode !== 'view'"
                type="text"
                size="small"
                class="delete-btn"
                @click="removeComponent(componentIndex)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>

            <!-- 组件基本信息 -->
            <div class="item-content">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item
                    label="组件名称"
                    :prop="`components.${componentIndex}.component_name`"
                    :rules="[{ required: true, message: '请输入组件名称', trigger: 'blur' }]"
                  >
                    <el-input v-model="component.component_name" placeholder="请输入组件名称" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item
                    label="组件料号"
                    :prop="`components.${componentIndex}.component_part_number`"
                    :rules="[{ required: true, message: '请输入组件料号', trigger: 'blur' }]"
                  >
                    <el-input v-model="component.component_part_number" placeholder="请输入组件料号" />
                  </el-form-item>
                </el-col>
              </el-row>

              <!-- 子组件信息 -->
              <div class="sub-components-section">
                <div class="sub-section-header">
                  <span class="sub-section-title">子组件</span>
                  <el-button
                    v-if="mode !== 'view'"
                    type="primary"
                    size="small"
                    plain
                    @click="addSubComponent(componentIndex)"
                    class="add-btn"
                  >
                    <el-icon><Plus /></el-icon>
                    添加子组件
                  </el-button>
                </div>

                <div
                  v-if="component.sub_components && component.sub_components.length > 0"
                  class="sub-components-list"
                >
                  <div
                    v-for="(subComponent, subIndex) in component.sub_components"
                    :key="subIndex"
                    class="sub-component-item"
                  >
                    <!-- 子组件标题栏 -->
                    <div class="item-header sub-component-header">
                      <div class="header-left">
                        <span class="item-number">{{ componentIndex + 1 }}.{{ subIndex + 1 }}</span>
                        <span class="item-title">子组件</span>
                      </div>
                      <el-button
                        v-if="mode !== 'view'"
                        type="text"
                        size="small"
                        class="delete-btn"
                        @click="removeSubComponent(componentIndex, subIndex)"
                      >
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </div>

                    <!-- 子组件内容 -->
                    <div class="item-content sub-component-content">
                      <el-row :gutter="20">
                        <el-col :span="8">
                          <el-form-item
                            label="子组件名称"
                            :prop="`components.${componentIndex}.sub_components.${subIndex}.sub_component_name`"
                            :rules="[{ required: true, message: '请输入子组件名称', trigger: 'blur' }]"
                          >
                            <el-input v-model="subComponent.sub_component_name" placeholder="请输入子组件名称" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="8">
                          <el-form-item
                            label="子组件料号"
                            :prop="`components.${componentIndex}.sub_components.${subIndex}.sub_component_part_number`"
                            :rules="[{ required: true, message: '请输入子组件料号', trigger: 'blur' }]"
                          >
                            <el-input v-model="subComponent.sub_component_part_number" placeholder="请输入子组件料号" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="8">
                          <el-form-item label="规格型号">
                            <el-input v-model="subComponent.specification" placeholder="请输入规格型号" />
                          </el-form-item>
                        </el-col>
                      </el-row>

                      <!-- 软件信息 -->
                      <div class="softwares-section">
                        <div class="sub-section-header">
                          <span class="sub-section-title">软件信息</span>
                          <el-button
                            v-if="mode !== 'view'"
                            type="primary"
                            size="small"
                            plain
                            @click="addSoftware(componentIndex, subIndex)"
                            class="add-btn"
                          >
                            <el-icon><Plus /></el-icon>
                            添加软件
                          </el-button>
                        </div>

                        <div
                          v-if="subComponent.softwares && subComponent.softwares.length > 0"
                          class="softwares-list"
                        >
                          <div
                            v-for="(software, softwareIndex) in subComponent.softwares"
                            :key="softwareIndex"
                            class="software-item"
                          >
                            <div class="software-header">
                              <span class="software-label">软件 {{ softwareIndex + 1 }}</span>
                              <el-button
                                v-if="mode !== 'view'"
                                type="text"
                                size="small"
                                class="delete-btn"
                                @click="removeSoftware(componentIndex, subIndex, softwareIndex)"
                              >
                                <el-icon><Delete /></el-icon>
                                删除
                              </el-button>
                            </div>

                            <div class="software-content">
                              <el-row :gutter="16">
                                <el-col :span="8">
                                  <el-form-item
                                    label="软件名称"
                                    :prop="`components.${componentIndex}.sub_components.${subIndex}.softwares.${softwareIndex}.software_name`"
                                    :rules="[{ required: true, message: '请输入软件名称', trigger: 'blur' }]"
                                  >
                                    <el-input v-model="software.software_name" placeholder="请输入软件名称" />
                                  </el-form-item>
                                </el-col>
                                <el-col :span="8">
                                  <el-form-item
                                    label="软件版本"
                                    :prop="`components.${componentIndex}.sub_components.${subIndex}.softwares.${softwareIndex}.software_version`"
                                  >
                                    <el-input v-model="software.software_version" placeholder="请输入软件版本" />
                                  </el-form-item>
                                </el-col>
                                <el-col :span="8">
                                  <el-form-item label="附件">
                                    <el-input v-model="software.attachment" placeholder="请输入附件名称" />
                                  </el-form-item>
                                </el-col>
                              </el-row>
                            </div>
                          </div>
                        </div>

                        <div v-else class="empty-softwares">
                          <el-empty description="暂无软件信息" :image-size="60" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else class="empty-sub-components">
                  <el-empty description="暂无子组件信息" :image-size="60" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-components">
          <el-empty description="暂无组件信息" />
        </div>
      </div>
    </el-form>
  </BaseDialog>

  <!-- 主从结构模式 -->
  <el-dialog
    v-if="useMasterDetail"
    :model-value="modelValue"
    :title="dialogTitle"
    width="1200px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <OrderMasterDetailEditor
      :model-value="modelValue"
      :is-edit="isEdit"
      :initial-data="initialData"
      @update:model-value="$emit('update:modelValue', $event)"
      @submit="handleMasterDetailSubmit"
    />
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete, QuestionFilled } from '@element-plus/icons-vue'
import BaseDialog from '@/components/base/BaseDialog.vue'
import OrderMasterDetailEditor from '@/components/order/OrderMasterDetailEditor.vue'
import { getOrderTemplate, getEmptyOrderData } from '@/config/orderTemplate'
const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  isEdit: {
    type: Boolean,
    default: false,
  },
  isView: {
    type: Boolean,
    default: false,
  },
  initialData: {
    type: Object,
    default: () => ({}),
  },
  editBasicOnly: {
    type: Boolean,
    default: false,
  },
  useMasterDetail: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'submit'])

// 表单引用
const formRef = ref(null)
const loading = ref(false)

// 计算属性
const mode = computed(() => {
  if (props.isView) return 'view'
  if (props.initialData && Object.keys(props.initialData).length > 0) {
    return props.isEdit ? 'edit' : 'view'
  }
  return 'create'
})

// 是否显示组件编辑区域
const showComponentSection = computed(() => {
  return mode.value !== 'view' && !props.editBasicOnly
})

const dialogTitle = computed(() => {
  if (mode.value === 'create') {
    return '添加订单'
  } else if (mode.value === 'view') {
    return '查看订单'
  } else if (mode.value === 'edit') {
    // 根据editBasicOnly属性决定标题
    return props.editBasicOnly ? '修改基本信息' : '编辑订单'
  }
  return '编辑订单'
})

// 表单数据
const formData = ref({
  order_number: '',
  model: '',
  part_number: '',
  serial_number_start: '',
  serial_number_end: '',
  serial_number_range: '',
  order_created_at: '',
  remark: '',
  components: []
})

// 表单验证规则
const formRules = {
  order_number: [
    { required: true, message: '请输入订单号', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请输入机型', trigger: 'blur' }
  ],
  part_number: [
    { required: true, message: '请输入料号', trigger: 'blur' }
  ],
  serial_number_range: [
    { required: true, message: '请输入序列号范围', trigger: 'blur' },
    {
      pattern: /^.+(--|~|-).*$/,
      message: '请输入正确的序列号范围格式，如：SNX1001-SNX1100 或 SNX1001~SNX1100',
      trigger: 'blur'
    }
  ]
}

// 处理序列号范围变化
const handleSerialNumberRangeChange = () => {
  const range = formData.value.serial_number_range
  if (range) {
    // 支持多种分隔符：-、--、~
    let separator = null
    let parts = []

    if (range.includes('--')) {
      separator = '--'
      parts = range.split('--')
    } else if (range.includes('~')) {
      separator = '~'
      parts = range.split('~')
    } else if (range.includes('-')) {
      separator = '-'
      parts = range.split('-')
    }

    if (separator && parts.length >= 2) {
      const start = parts[0].trim()
      const end = parts[parts.length - 1].trim() // 取最后一部分作为结束
      formData.value.serial_number_start = start
      formData.value.serial_number_end = end
    }
  }
}

// 重置表单
const resetForm = () => {
  formData.value = {
    order_number: '',
    model: '',
    part_number: '',
    serial_number_start: '',
    serial_number_end: '',
    serial_number_range: '',
    order_created_at: '',
    remark: '',
    components: []
  }
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

// 监听初始数据变化
watch(
  () => props.initialData,
  (newData) => {
    if (newData && Object.keys(newData).length > 0) {
      formData.value = {
        ...newData,
        components: newData.components || []
      }

      // 合并序列号范围
      if (newData.serial_number_start && newData.serial_number_end) {
        formData.value.serial_number_range = `${newData.serial_number_start}-${newData.serial_number_end}`
      }
    } else {
      // 创建模式下默认加载模板
      if (mode.value === 'create') {
        const template = getOrderTemplate()
        formData.value = { ...template }

        // 合并序列号范围
        if (template.serial_number_start && template.serial_number_end) {
          formData.value.serial_number_range = `${template.serial_number_start}-${template.serial_number_end}`
        }
      } else {
        resetForm()
      }
    }
  },
  { immediate: true, deep: true }
)

// 监听弹窗显示状态
watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      nextTick(() => {
        formRef.value?.clearValidate()
      })
    }
  }
)

// 添加组件
const addComponent = () => {
  formData.value.components.push({
    component_name: '',
    component_part_number: '',
    sub_components: []
  })
}

// 删除组件
const removeComponent = (index) => {
  formData.value.components.splice(index, 1)
}

// 添加子组件
const addSubComponent = (componentIndex) => {
  if (!formData.value.components[componentIndex].sub_components) {
    formData.value.components[componentIndex].sub_components = []
  }
  formData.value.components[componentIndex].sub_components.push({
    sub_component_name: '',
    sub_component_part_number: '',
    specification: '',
    softwares: []
  })
}

// 删除子组件
const removeSubComponent = (componentIndex, subIndex) => {
  formData.value.components[componentIndex].sub_components.splice(subIndex, 1)
}

// 添加软件
const addSoftware = (componentIndex, subIndex) => {
  if (!formData.value.components[componentIndex].sub_components[subIndex].softwares) {
    formData.value.components[componentIndex].sub_components[subIndex].softwares = []
  }
  formData.value.components[componentIndex].sub_components[subIndex].softwares.push({
    software_name: '',
    software_version: '',
    attachment: ''
  })
}

// 删除软件
const removeSoftware = (componentIndex, subIndex, softwareIndex) => {
  formData.value.components[componentIndex].sub_components[subIndex].softwares.splice(softwareIndex, 1)
}

// 确认提交
const handleConfirm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    let submitData

    if (props.editBasicOnly) {
      // 只编辑基本信息，不包含组件树
      submitData = {
        order_number: formData.value.order_number,
        model: formData.value.model,
        part_number: formData.value.part_number,
        serial_number_start: formData.value.serial_number_start,
        serial_number_end: formData.value.serial_number_end,
        order_created_at: formData.value.order_created_at || null,
        remark: formData.value.remark || null,
      }
    } else {
      // 完整编辑，包含组件树
      submitData = {
        ...formData.value,
        components: formData.value.components
          .filter(component => component.component_name && component.component_part_number)
          .map(component => ({
            ...component,
            sub_components: (component.sub_components || [])
              .filter(subComponent => subComponent.sub_component_name && subComponent.sub_component_part_number)
              .map(subComponent => ({
                ...subComponent,
                softwares: (subComponent.softwares || [])
                  .filter(software => software.software_name)
              }))
          }))
      }
    }

    emit('submit', submitData)
  } catch (error) {
    console.error('表单验证失败:', error)
    ElMessage.error('请检查表单填写是否正确')
  }
}

// 加载模板数据
const loadTemplate = () => {
  const template = getOrderTemplate()
  formData.value = { ...template }

  // 合并序列号范围
  if (template.serial_number_start && template.serial_number_end) {
    formData.value.serial_number_range = `${template.serial_number_start}-${template.serial_number_end}`
  }

  ElMessage.success('模板数据已加载')
}

// 清除所有数据
const clearAllData = () => {
  const emptyData = getEmptyOrderData()
  formData.value = { ...emptyData }

  nextTick(() => {
    formRef.value?.clearValidate()
  })

  ElMessage.success('所有信息已清除')
}

// 取消操作
const handleCancel = () => {
  emit('update:modelValue', false)
  resetForm()
}

// 主从结构模式的提交处理
const handleMasterDetailSubmit = (orderData) => {
  emit('submit', orderData)
}
</script>

<style scoped>
/* 基础布局 */
.form-section {
  margin-bottom: 32px;
}

/* 模板操作按钮 */
.template-actions {
  margin-bottom: 20px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  display: flex;
  gap: 12px;
  align-items: center;
}

.form-content {
  padding: 20px 0;
}

/* 标题样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f2f5;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.sub-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
}

.sub-section-title {
  font-size: 14px;
  font-weight: 500;
  color: #595959;
}

/* 组件容器 */
.components-container {
  padding: 0;
}

.component-item {
  margin-bottom: 24px;
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

/* 项目标题栏 */
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e8e8e8;
}

.component-header {
  background: #e6f7ff;
  border-bottom: 1px solid #91d5ff;
}

.sub-component-header {
  background: #f6ffed;
  border-bottom: 1px solid #b7eb8f;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #1890ff;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
}

.sub-component-header .item-number {
  background: #52c41a;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

/* 内容区域 */
.item-content {
  padding: 20px 16px;
}

.sub-component-content {
  background: #fcfcfc;
}

.sub-components-section {
  margin-top: 20px;
}

.sub-component-item {
  margin-bottom: 16px;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  overflow: hidden;
}

/* 软件信息 */
.softwares-section {
  margin-top: 20px;
}

.software-item {
  margin-bottom: 16px;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  overflow: hidden;
}

.software-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f9f9f9;
  border-bottom: 1px solid #e8e8e8;
}

.software-label {
  font-size: 13px;
  font-weight: 500;
  color: #595959;
}

.software-content {
  padding: 16px 12px;
}

/* 按钮样式 */
.add-btn {
  border-radius: 6px;
  font-size: 13px;
}

.delete-btn {
  color: #ff4d4f;
  padding: 4px 8px;
  font-size: 13px;
}

.delete-btn:hover {
  background: #fff2f0;
  color: #ff4d4f;
}

/* 空状态 */
.empty-components,
.empty-sub-components,
.empty-softwares {
  text-align: center;
  padding: 40px 20px;
  color: #8c8c8c;
  background: #fafafa;
  border-radius: 6px;
  margin: 16px 0;
  border: 1px dashed #d9d9d9;
}

/* 表单项优化 */
.el-form-item {
  margin-bottom: 18px;
}

.el-form-item__label {
  font-weight: 500;
  color: #262626;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .section-title {
    font-size: 16px;
  }

  .item-content {
    padding: 16px 12px;
  }

  .software-content {
    padding: 12px 8px;
  }

  .item-header {
    padding: 10px 12px;
  }
}
</style>
