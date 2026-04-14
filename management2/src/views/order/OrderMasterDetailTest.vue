<template>
  <div class="test-container">
    <div class="test-header">
      <h2>订单主从结构编辑器测试</h2>
      <div class="test-actions">
        <el-button type="primary" @click="openNewOrder">添加订单（主从结构）</el-button>
        <el-button type="success" @click="openEditOrder">编辑订单（主从结构）</el-button>
        <el-button @click="openBasicEdit">基本信息编辑</el-button>
      </div>
    </div>

    <!-- 主从结构编辑器 -->
    <OrderMasterDetailEditor
      v-model="masterDetailVisible"
      :is-edit="isEdit"
      :initial-data="testOrderData"
      @submit="handleSubmit"
    />

    <!-- 传统编辑对话框 -->
    <OrderFormDialog
      v-model="basicEditVisible"
      :is-edit="true"
      :edit-basic-only="true"
      :initial-data="testOrderData"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import OrderMasterDetailEditor from '@/components/order/OrderMasterDetailEditor.vue'
import OrderFormDialog from '@/components/dialog/OrderFormDialog.vue'

// 响应式数据
const masterDetailVisible = ref(false)
const basicEditVisible = ref(false)
const isEdit = ref(false)

// // 测试数据
// const testOrderData = ref({
//   order_number: 'TEST-ORDER-001',
//   model: 'Model-X1',
//   part_number: 'PN-X1-001',
//   serial_number_start: 'SNX1001',
//   serial_number_end: 'SNX1100',
//   components: [
//     {
//       component_name: 'MainBoard',
//       component_part_number: 'COMP-X1-100',
//       sub_components: [
//         {
//           sub_component_name: 'CPU-Module',
//           sub_component_part_number: 'SUB-X1-CPU-100',
//           specification: 'ARMv8-A',
//           softwares: [
//             {
//               software_name: 'Bootloader',
//               software_version: '1.0.0',
//               attachment: 'bootloader_1.0.0.bin'
//             }
//           ]
//         }
//       ]
//     }
//   ]
// })

// 方法
const openNewOrder = () => {
  isEdit.value = false
  testOrderData.value = {
    order_number: '',
    model: '',
    part_number: '',
    serial_number_start: '',
    serial_number_end: '',
    components: []
  }
  masterDetailVisible.value = true
}

const openEditOrder = () => {
  isEdit.value = true
  masterDetailVisible.value = true
}

const openBasicEdit = () => {
  basicEditVisible.value = true
}

const handleSubmit = (orderData) => {
  console.log('提交订单数据:', orderData)
  ElMessage.success('订单保存成功')
  
  // 关闭对话框
  masterDetailVisible.value = false
  basicEditVisible.value = false
}
</script>

<style scoped>
.test-container {
  padding: 20px;
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.test-actions {
  display: flex;
  gap: 12px;
}
</style>
