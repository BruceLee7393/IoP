<template>
  <div class="order-structure-tree">
    <el-tree
      ref="treeRef"
      :data="treeData"
      :props="treeProps"
      :expand-on-click-node="false"
      :highlight-current="true"
      node-key="id"
      default-expand-all
      @node-click="handleNodeClick"
    >
      <template #default="{ node, data }">
        <div class="tree-node">
          <div class="node-content">
            <span class="node-label">{{ data.label }}</span>
            <span v-if="data.status" class="node-status" :class="`status-${data.status}`">
              {{ getStatusText(data.status) }}
            </span>
          </div>
          <div class="node-actions">
            <el-button
              v-if="canAddChild(data)"
              size="small"
              type="primary"
              :icon="Plus"
              circle
              @click.stop="handleAddChild(data)"
            />
            <el-button
              v-if="canDelete(data)"
              size="small"
              type="danger"
              :icon="Delete"
              circle
              @click.stop="handleDelete(data)"
            />
          </div>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const props = defineProps({
  orderData: {
    type: Object,
    required: true,
  },
  selectedNode: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['node-select', 'node-add', 'node-delete'])

const treeRef = ref(null)

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'label',
}

// 验证订单基本信息是否完整
const validateOrderBasicInfo = (orderData) => {
  return !!(
    orderData.order_number &&
    orderData.model &&
    orderData.part_number &&
    orderData.serial_number_start &&
    orderData.serial_number_end
  )
}

// 验证组件信息是否完整
const validateComponentInfo = (component) => {
  return !!(
    component.component_name &&
    component.component_part_number
  )
}

// 验证子组件信息是否完整
const validateSubComponentInfo = (subComponent) => {
  return !!(
    subComponent.sub_component_name &&
    subComponent.sub_component_part_number
  )
}

// 验证软件信息是否完整
const validateSoftwareInfo = (software) => {
  return !!(
    software.software_name &&
    software.software_version
  )
}

// 将订单数据转换为树形结构
const treeData = computed(() => {
  const orderBasicComplete = validateOrderBasicInfo(props.orderData)

  const orderNode = {
    id: 'order-root',
    type: 'order',
    label: `订单: ${props.orderData.order_number || '新订单'}`,
    status: orderBasicComplete ? 'complete' : 'incomplete',
    data: {
      order_number: props.orderData.order_number,
      model: props.orderData.model,
      part_number: props.orderData.part_number,
      serial_number_start: props.orderData.serial_number_start,
      serial_number_end: props.orderData.serial_number_end,
    },
    children: []
  }

  // 添加组件节点
  if (props.orderData.components && props.orderData.components.length > 0) {
    orderNode.children = props.orderData.components.map((component, componentIndex) => {
      const componentComplete = validateComponentInfo(component)

      const componentNode = {
        id: `component-${componentIndex}`,
        type: 'component',
        label: component.component_name || `组件 ${componentIndex + 1}`,
        status: componentComplete ? 'complete' : 'incomplete',
        data: component,
        children: []
      }

      // 添加子组件节点
      if (component.sub_components && component.sub_components.length > 0) {
        componentNode.children = component.sub_components.map((subComponent, subIndex) => {
          const subComponentComplete = validateSubComponentInfo(subComponent)

          const subComponentNode = {
            id: `subcomponent-${componentIndex}-${subIndex}`,
            type: 'subComponent',
            label: subComponent.sub_component_name || `子组件 ${subIndex + 1}`,
            status: subComponentComplete ? 'complete' : 'incomplete',
            data: subComponent,
            children: []
          }

          // 添加软件节点
          if (subComponent.softwares && subComponent.softwares.length > 0) {
            subComponentNode.children = subComponent.softwares.map((software, softwareIndex) => {
              const softwareComplete = validateSoftwareInfo(software)

              return {
                id: `software-${componentIndex}-${subIndex}-${softwareIndex}`,
                type: 'software',
                label: software.software_name || `软件 ${softwareIndex + 1}`,
                status: softwareComplete ? 'complete' : 'incomplete',
                data: software,
                children: []
              }
            })
          }

          return subComponentNode
        })
      }

      return componentNode
    })
  }

  return [orderNode]
})



// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    complete: '完成',
    incomplete: '未完成',
    editing: '编辑中'
  }
  return statusMap[status] || ''
}

// 判断是否可以添加子节点
const canAddChild = (nodeData) => {
  return nodeData.type === 'component' || nodeData.type === 'subComponent'
}

// 判断是否可以删除节点
const canDelete = (nodeData) => {
  return nodeData.type !== 'order'
}

// 事件处理
const handleNodeClick = (nodeData) => {
  emit('node-select', nodeData)
}

const handleAddChild = (parentNode) => {
  const childType = parentNode.type === 'component' ? 'subComponent' : 'software'
  emit('node-add', parentNode, childType)
}

const handleDelete = async (nodeData) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 "${nodeData.label}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    emit('node-delete', nodeData)
  } catch {
    // 用户取消删除
  }
}

// 监听选中节点变化，同步树的当前节点
watch(() => props.selectedNode, (newNode) => {
  if (newNode && treeRef.value) {
    treeRef.value.setCurrentKey(newNode.id)
  }
}, { immediate: true })
</script>

<style scoped>
.order-structure-tree {
  height: 100%;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 4px 0;
}

.node-content {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.node-label {
  flex: 1;
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-status {
  margin-left: 8px;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-complete {
  background-color: #f0f9ff;
  color: #059669;
}

.status-incomplete {
  background-color: #fef3c7;
  color: #d97706;
}

.status-editing {
  background-color: #dbeafe;
  color: #2563eb;
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

:deep(.el-tree-node__content) {
  padding: 8px 0;
}

:deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: #ecf5ff;
  color: #409eff;
}
</style>
