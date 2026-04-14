<template>
  <div class="order-master-detail-editor">
    <!-- 模板操作区域 -->
    <div v-if="!isEdit" class="template-actions">
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

    <!-- 主从布局容器 -->
    <div class="master-detail-container">
      <!-- 左栏：Master区域 - 订单结构树 -->
      <div class="master-panel">
        <div class="panel-header">
          <h4 class="panel-title">订单结构</h4>
          <div class="panel-actions">
            <el-button 
              size="small" 
              type="primary" 
              :icon="Plus"
              @click="handleAddRootComponent"
              :disabled="!canAddComponent"
            >
              添加组件
            </el-button>
          </div>
        </div>
        <div class="panel-content">
          <OrderStructureTree
            :order-data="orderData"
            :selected-node="selectedNode"
            @node-select="handleNodeSelect"
            @node-add="handleNodeAdd"
            @node-delete="handleNodeDelete"
          />
        </div>
      </div>

      <!-- 右栏：Detail区域 - 动态表单 -->
      <div class="detail-panel">
        <div class="panel-header">
          <h4 class="panel-title">{{ currentFormTitle }}</h4>
          <div class="panel-actions">
            <el-button 
              v-if="canAddSubItem"
              size="small" 
              type="success"
              :icon="Plus"
              @click="handleAddSubItem"
            >
              {{ addSubItemLabel }}
            </el-button>
            <el-button 
              v-if="canDeleteCurrentNode"
              size="small" 
              type="danger"
              :icon="Delete"
              @click="handleDeleteCurrentNode"
            >
              删除
            </el-button>
          </div>
        </div>
        <div class="panel-content">
          <OrderDynamicForm
            :node-type="selectedNode?.type || 'order'"
            :form-data="currentFormData"
            :rules="currentFormRules"
            @form-change="handleFormChange"
            @form-validate="handleFormValidate"
          />
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="editor-footer">
      <div class="footer-actions">
        <el-button @click="handleCancel">取消</el-button>
        <el-button 
          type="primary" 
          :loading="saving"
          @click="handleSave"
        >
          保存订单
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import OrderStructureTree from './OrderStructureTree.vue'
import OrderDynamicForm from './OrderDynamicForm.vue'
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
  initialData: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:modelValue', 'submit'])

// 响应式数据
const saving = ref(false)
const selectedNode = ref(null)
const orderData = ref({
  order_number: '',
  model: '',
  part_number: '',
  serial_number_start: '',
  serial_number_end: '',
  order_created_at: '',
  remark: '',
  components: []
})

// 计算属性
const currentFormTitle = computed(() => {
  if (!selectedNode.value) return '订单基本信息'
  
  const titleMap = {
    order: '订单基本信息',
    component: '组件信息',
    subComponent: '子组件信息',
    software: '软件信息'
  }
  
  return titleMap[selectedNode.value.type] || '编辑信息'
})

const currentFormData = computed(() => {
  if (!selectedNode.value) {
    // 返回订单基本信息
    return {
      order_number: orderData.value.order_number,
      model: orderData.value.model,
      part_number: orderData.value.part_number,
      serial_number_start: orderData.value.serial_number_start,
      serial_number_end: orderData.value.serial_number_end,
      order_created_at: orderData.value.order_created_at,
      remark: orderData.value.remark,
    }
  }

  // 根据选中节点返回对应数据
  return selectedNode.value.data || {}
})

const currentFormRules = computed(() => {
  const nodeType = selectedNode.value?.type || 'order'
  
  const rulesMap = {
    order: {
      order_number: [{ required: true, message: '请输入订单号', trigger: 'blur' }],
      model: [{ required: true, message: '请输入机型', trigger: 'blur' }],
      part_number: [{ required: true, message: '请输入料号', trigger: 'blur' }],
      serial_number_range: [
        { required: true, message: '请输入序列号范围', trigger: 'blur' },
        {
          pattern: /^.+(--|~|-).*$/,
          message: '请输入正确的序列号范围格式，如：SNX1001-SNX1100 或 SNX1001~SNX1100',
          trigger: 'blur'
        }
      ],
    },
    component: {
      component_name: [{ required: true, message: '请输入组件名称', trigger: 'blur' }],
      component_part_number: [{ required: true, message: '请输入组件料号', trigger: 'blur' }],
    },
    subComponent: {
      sub_component_name: [{ required: true, message: '请输入子组件名称', trigger: 'blur' }],
      sub_component_part_number: [{ required: true, message: '请输入子组件料号', trigger: 'blur' }],
      specification: [{ required: false, message: '请输入规格', trigger: 'blur' }],
    },
    software: {
      software_name: [{ required: true, message: '请输入软件名称', trigger: 'blur' }],
      software_version: [{ required: true, message: '请输入软件版本', trigger: 'blur' }],
      attachment: [{ required: false, message: '请输入附件', trigger: 'blur' }],
    }
  }
  
  return rulesMap[nodeType] || {}
})

const canAddComponent = computed(() => {
  // 订单基本信息填写完整后才能添加组件
  return orderData.value.order_number &&
         orderData.value.model &&
         orderData.value.part_number &&
         orderData.value.serial_number_start &&
         orderData.value.serial_number_end
})

const canAddSubItem = computed(() => {
  if (!selectedNode.value) return false
  
  const nodeType = selectedNode.value.type
  return nodeType === 'component' || nodeType === 'subComponent'
})

const addSubItemLabel = computed(() => {
  if (!selectedNode.value) return ''
  
  const labelMap = {
    component: '添加子组件',
    subComponent: '添加软件'
  }
  
  return labelMap[selectedNode.value.type] || ''
})

const canDeleteCurrentNode = computed(() => {
  return selectedNode.value && selectedNode.value.type !== 'order'
})

// 方法
const handleNodeSelect = (node) => {
  selectedNode.value = node
}

const handleNodeAdd = (parentNode, nodeType) => {
  // 创建新节点的默认数据
  const newNodeData = createDefaultNodeData(nodeType)
  let newNodeId = ''

  if (nodeType === 'component') {
    // 添加根级组件
    orderData.value.components.push(newNodeData)
    newNodeId = `component-${orderData.value.components.length - 1}`
  } else if (nodeType === 'subComponent' && parentNode) {
    // 添加子组件到指定组件
    const componentIndex = getComponentIndex(parentNode.id)
    if (componentIndex !== -1) {
      if (!orderData.value.components[componentIndex].sub_components) {
        orderData.value.components[componentIndex].sub_components = []
      }
      orderData.value.components[componentIndex].sub_components.push(newNodeData)
      const subComponentIndex = orderData.value.components[componentIndex].sub_components.length - 1
      newNodeId = `subcomponent-${componentIndex}-${subComponentIndex}`
    }
  } else if (nodeType === 'software' && parentNode) {
    // 添加软件到指定子组件
    const { componentIndex, subComponentIndex } = getSubComponentIndex(parentNode.id)
    if (componentIndex !== -1 && subComponentIndex !== -1) {
      if (!orderData.value.components[componentIndex].sub_components[subComponentIndex].softwares) {
        orderData.value.components[componentIndex].sub_components[subComponentIndex].softwares = []
      }
      orderData.value.components[componentIndex].sub_components[subComponentIndex].softwares.push(newNodeData)
      const softwareIndex = orderData.value.components[componentIndex].sub_components[subComponentIndex].softwares.length - 1
      newNodeId = `software-${componentIndex}-${subComponentIndex}-${softwareIndex}`
    }
  }

  // 选中新添加的节点
  nextTick(() => {
    // 创建新节点对象并选中
    selectedNode.value = {
      type: nodeType,
      id: newNodeId,
      label: getNodeLabel(nodeType, newNodeData),
      data: newNodeData
    }
  })
}

const handleNodeDelete = (node) => {
  const nodeType = node.type
  const nodeId = node.id

  if (nodeType === 'component') {
    const componentIndex = getComponentIndex(nodeId)
    if (componentIndex !== -1) {
      orderData.value.components.splice(componentIndex, 1)
    }
  } else if (nodeType === 'subComponent') {
    const { componentIndex, subComponentIndex } = getSubComponentIndex(nodeId)
    if (componentIndex !== -1 && subComponentIndex !== -1) {
      orderData.value.components[componentIndex].sub_components.splice(subComponentIndex, 1)
    }
  } else if (nodeType === 'software') {
    const { componentIndex, subComponentIndex, softwareIndex } = getSoftwareIndex(nodeId)
    if (componentIndex !== -1 && subComponentIndex !== -1 && softwareIndex !== -1) {
      orderData.value.components[componentIndex].sub_components[subComponentIndex].softwares.splice(softwareIndex, 1)
    }
  }

  // 删除后选中订单根节点
  selectedNode.value = {
    type: 'order',
    id: 'order-root',
    label: '订单基本信息',
    data: orderData.value
  }
}

const handleAddRootComponent = () => {
  // 添加根级组件
  handleNodeAdd(null, 'component')
}

const handleAddSubItem = () => {
  if (!selectedNode.value) return
  
  const nodeType = selectedNode.value.type === 'component' ? 'subComponent' : 'software'
  handleNodeAdd(selectedNode.value, nodeType)
}

const handleDeleteCurrentNode = () => {
  if (selectedNode.value) {
    handleNodeDelete(selectedNode.value)
  }
}

const handleFormChange = (formData) => {
  if (!selectedNode.value) return

  if (selectedNode.value.type === 'order') {
    // 更新订单基本信息
    Object.assign(orderData.value, formData)
    // 同步更新selectedNode的data
    selectedNode.value.data = { ...orderData.value }
  } else {
    // 更新选中节点的数据
    const nodeType = selectedNode.value.type
    const nodeId = selectedNode.value.id

    if (nodeType === 'component') {
      const componentIndex = getComponentIndex(nodeId)
      if (componentIndex !== -1) {
        Object.assign(orderData.value.components[componentIndex], formData)
        // 同步更新selectedNode的data
        selectedNode.value.data = { ...orderData.value.components[componentIndex] }
        // 更新节点标签
        selectedNode.value.label = getNodeLabel(nodeType, selectedNode.value.data)
      }
    } else if (nodeType === 'subComponent') {
      const { componentIndex, subComponentIndex } = getSubComponentIndex(nodeId)
      if (componentIndex !== -1 && subComponentIndex !== -1) {
        Object.assign(orderData.value.components[componentIndex].sub_components[subComponentIndex], formData)
        // 同步更新selectedNode的data
        selectedNode.value.data = { ...orderData.value.components[componentIndex].sub_components[subComponentIndex] }
        // 更新节点标签
        selectedNode.value.label = getNodeLabel(nodeType, selectedNode.value.data)
      }
    } else if (nodeType === 'software') {
      const { componentIndex, subComponentIndex, softwareIndex } = getSoftwareIndex(nodeId)
      if (componentIndex !== -1 && subComponentIndex !== -1 && softwareIndex !== -1) {
        Object.assign(orderData.value.components[componentIndex].sub_components[subComponentIndex].softwares[softwareIndex], formData)
        // 同步更新selectedNode的data
        selectedNode.value.data = { ...orderData.value.components[componentIndex].sub_components[subComponentIndex].softwares[softwareIndex] }
        // 更新节点标签
        selectedNode.value.label = getNodeLabel(nodeType, selectedNode.value.data)
      }
    }
  }
}

const handleFormValidate = (validationResult) => {
  // 处理表单验证结果
  console.log('表单验证结果:', validationResult)
}

// 调试：监听orderData变化
watch(() => orderData.value, (newData) => {
  console.log('OrderMasterDetailEditor - orderData变化:', newData)
}, { deep: true })

// 加载模板数据
const loadTemplate = () => {
  const template = getOrderTemplate()
  orderData.value = { ...template }

  // 重新选中订单根节点
  selectedNode.value = {
    type: 'order',
    id: 'order-root',
    label: '订单基本信息',
    data: orderData.value
  }

  ElMessage.success('模板数据已加载')
}

// 清除所有数据
const clearAllData = () => {
  const emptyData = getEmptyOrderData()
  orderData.value = { ...emptyData }

  // 重新选中订单根节点
  selectedNode.value = {
    type: 'order',
    id: 'order-root',
    label: '订单基本信息',
    data: orderData.value
  }

  ElMessage.success('所有信息已清除')
}

const handleCancel = () => {
  emit('update:modelValue', false)
}

const handleSave = async () => {
  try {
    saving.value = true

    // 验证整个订单数据
    const isValid = await validateAllForms()
    if (!isValid) {
      ElMessage.error('请检查表单填写是否正确')
      return
    }

    // 清理和格式化数据
    const cleanedData = cleanOrderData(orderData.value)

    emit('submit', cleanedData)
  } catch (error) {
    console.error('保存订单失败:', error)
    ElMessage.error('保存订单失败')
  } finally {
    saving.value = false
  }
}

// 辅助工具方法
const createDefaultNodeData = (nodeType) => {
  const defaultData = {
    component: {
      component_name: '',
      component_part_number: '',
      sub_components: []
    },
    subComponent: {
      sub_component_name: '',
      sub_component_part_number: '',
      specification: '',
      softwares: []
    },
    software: {
      software_name: '',
      software_version: '',
      attachment: ''
    }
  }

  return { ...defaultData[nodeType] }
}

const getComponentIndex = (nodeId) => {
  const match = nodeId.match(/component-(\d+)/)
  return match ? parseInt(match[1]) : -1
}

const getSubComponentIndex = (nodeId) => {
  const match = nodeId.match(/subcomponent-(\d+)-(\d+)/)
  return match ? {
    componentIndex: parseInt(match[1]),
    subComponentIndex: parseInt(match[2])
  } : { componentIndex: -1, subComponentIndex: -1 }
}

const getSoftwareIndex = (nodeId) => {
  const match = nodeId.match(/software-(\d+)-(\d+)-(\d+)/)
  return match ? {
    componentIndex: parseInt(match[1]),
    subComponentIndex: parseInt(match[2]),
    softwareIndex: parseInt(match[3])
  } : { componentIndex: -1, subComponentIndex: -1, softwareIndex: -1 }
}

const getNodeLabel = (nodeType, nodeData) => {
  const labelMap = {
    component: nodeData.component_name || '新组件',
    subComponent: nodeData.sub_component_name || '新子组件',
    software: nodeData.software_name || '新软件'
  }
  return labelMap[nodeType] || '新节点'
}

const validateAllForms = async () => {
  // 验证所有必要的表单数据
  if (!orderData.value.order_number || !orderData.value.model || !orderData.value.part_number) {
    return false
  }

  // 验证组件数据
  for (const component of orderData.value.components) {
    if (!component.component_name || !component.component_part_number) {
      return false
    }

    // 验证子组件数据
    for (const subComponent of component.sub_components || []) {
      if (!subComponent.sub_component_name || !subComponent.sub_component_part_number) {
        return false
      }

      // 验证软件数据
      for (const software of subComponent.softwares || []) {
        if (!software.software_name || !software.software_version) {
          return false
        }
      }
    }
  }

  return true
}

const cleanOrderData = (data) => {
  // 清理和格式化订单数据，只保留后端需要的字段
  const cleanedData = {
    order_number: data.order_number,
    model: data.model,
    part_number: data.part_number,
    serial_number_start: data.serial_number_start,
    serial_number_end: data.serial_number_end,
    order_created_at: data.order_created_at || null,
    remark: data.remark || null,
    components: data.components
      .filter(component => component.component_name && component.component_part_number)
      .map(component => ({
        component_name: component.component_name,
        component_part_number: component.component_part_number,
        sub_components: (component.sub_components || [])
          .filter(subComponent => subComponent.sub_component_name && subComponent.sub_component_part_number)
          .map(subComponent => ({
            sub_component_name: subComponent.sub_component_name,
            sub_component_part_number: subComponent.sub_component_part_number,
            specification: subComponent.specification || '',
            softwares: (subComponent.softwares || [])
              .filter(software => software.software_name && software.software_version)
              .map(software => ({
                software_name: software.software_name,
                software_version: software.software_version,
                attachment: software.attachment || ''
              }))
          }))
      }))
  }

  console.log('清理后的订单数据:', cleanedData)
  return cleanedData
}

// 初始化数据
watch(() => props.modelValue, (visible) => {
  if (visible) {
    // 初始化订单数据
    if (props.initialData && Object.keys(props.initialData).length > 0) {
      orderData.value = { ...props.initialData }
    } else {
      // 创建模式下默认加载模板
      if (!props.isEdit) {
        const template = getOrderTemplate()
        orderData.value = { ...template }
      } else {
        // 编辑模式下重置为空数据
        orderData.value = {
          order_number: '',
          model: '',
          part_number: '',
          serial_number_start: '',
          serial_number_end: '',
          order_created_at: '',
          remark: '',
          components: []
        }
      }
    }
    
    // 默认选中订单根节点
    selectedNode.value = {
      type: 'order',
      id: 'order-root',
      label: '订单基本信息',
      data: orderData.value
    }
  }
}, { immediate: true })
</script>

<style scoped>
.order-master-detail-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.template-actions {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  display: flex;
  gap: 12px;
  align-items: center;
}

.master-detail-container {
  flex: 1;
  display: flex;
  height: 600px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.master-panel {
  width: 300px;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  background-color: #fafafa;
}

.detail-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
}

.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.panel-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.editor-footer {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  background-color: #f8f9fa;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
