// src/composables/cfg/useOrderDetailManagement.js
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import * as orderApi from '@/api/order'

/**
 * 订单详情管理配置
 */
export function useOrderDetailManagement() {
  const router = useRouter()
  
  // 响应式数据
  const loading = ref(false)
  const orderInfo = ref(null)
  
  // 获取订单ID
  const orderId = computed(() => {
    const route = router.currentRoute.value
    return route.params.id
  })

  // 格式化日期时间
  const formatDateTime = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  // 获取订单详情
  const fetchOrderDetail = async () => {
    try {
      loading.value = true
      const response = await orderApi.getOrderDetails(orderId.value)
      console.log('API响应数据:', response)

      // 处理API返回的数据结构
      if (response.code === 0 && response.data) {
        orderInfo.value = response.data
      } else {
        orderInfo.value = response.data || response
      }

      // 调试：检查软件附件信息
      if (orderInfo.value && orderInfo.value.components) {
        console.log('订单详情中的组件数据:', orderInfo.value.components)
        orderInfo.value.components.forEach((component, compIndex) => {
          if (component.sub_components) {
            component.sub_components.forEach((subComponent, subIndex) => {
              if (subComponent.softwares) {
                subComponent.softwares.forEach((software, softIndex) => {
                  console.log(`软件 [${compIndex}-${subIndex}-${softIndex}]:`, {
                    id: software.id,
                    name: software.software_name,
                    attachment: software.attachment,
                    appendix: software.appendix
                  })
                })
              }
            })
          }
        })
      }
    } catch (error) {
      console.error('获取订单详情失败:', error)
      ElMessage.error('获取订单详情失败')
      router.push('/order')
    } finally {
      loading.value = false
    }
  }

  // 数据预处理：将嵌套结构扁平化为表格行，实现Excel合并单元格效果
  const flattenedData = computed(() => {
    if (!orderInfo.value || !orderInfo.value.components) {
      return []
    }

    const result = []
    const components = orderInfo.value.components || []

    components.forEach((component, componentIndex) => {
      const subComponents = component.sub_components || []

      if (subComponents.length === 0) {
        // 组件没有子组件，创建一行显示组件信息
        result.push({
          component_name: component.component_name,
          component_part_number: component.component_part_number,
          sub_component_name: '-',
          sub_component_part_number: '-',
          specification: '-',
          software_name: '-',
          software_version: '-',
          attachment: '-',
          showComponent: true,
          showSubComponent: true,
          componentRowspan: 1,
          subComponentRowspan: 1,
        })
      } else {
        subComponents.forEach((subComponent, subIndex) => {
          const softwares = subComponent.softwares || []

          if (softwares.length === 0) {
            // 子组件没有软件，创建一行显示子组件信息
            result.push({
              component_name: component.component_name,
              component_part_number: component.component_part_number,
              sub_component_name: subComponent.sub_component_name,
              sub_component_part_number: subComponent.sub_component_part_number,
              specification: subComponent.specification,
              software_name: '-',
              software_version: '-',
              attachment: '-',
              showComponent: subIndex === 0,
              showSubComponent: true,
              componentRowspan: 1,
              subComponentRowspan: 1,
            })
          } else {
            softwares.forEach((software, softwareIndex) => {
              result.push({
                component_name: component.component_name,
                component_part_number: component.component_part_number,
                sub_component_name: subComponent.sub_component_name,
                sub_component_part_number: subComponent.sub_component_part_number,
                specification: subComponent.specification,
                software_name: software.software_name,
                software_version: software.software_version,
                attachment: software.attachment || software.appendix,
                software_id: software.id, // 添加软件ID
                showComponent: subIndex === 0 && softwareIndex === 0,
                showSubComponent: softwareIndex === 0,
                componentRowspan: 1,
                subComponentRowspan: 1,
              })
            })
          }
        })
      }
    })

    // 计算rowspan
    calculateRowspans(result)

    return result
  })

  // 计算rowspan值，实现Excel合并单元格效果
  const calculateRowspans = (data) => {
    if (data.length === 0) return

    // 计算组件的rowspan
    let currentComponent = null
    let componentStartIndex = 0

    data.forEach((item, index) => {
      const componentKey = `${item.component_name}-${item.component_part_number}`

      if (currentComponent !== componentKey) {
        // 新组件开始，计算上一个组件的rowspan
        if (currentComponent !== null) {
          const rowspan = index - componentStartIndex
          data[componentStartIndex].componentRowspan = rowspan
        }

        currentComponent = componentKey
        componentStartIndex = index
      }
    })

    // 处理最后一个组件
    if (currentComponent !== null) {
      const rowspan = data.length - componentStartIndex
      data[componentStartIndex].componentRowspan = rowspan
    }

    // 计算子组件的rowspan
    let currentSubComponent = null
    let subComponentStartIndex = 0

    data.forEach((item, index) => {
      const subComponentKey = `${item.component_name}-${item.component_part_number}-${item.sub_component_name}-${item.sub_component_part_number}`

      if (currentSubComponent !== subComponentKey) {
        // 新子组件开始，计算上一个子组件的rowspan
        if (currentSubComponent !== null) {
          const rowspan = index - subComponentStartIndex
          data[subComponentStartIndex].subComponentRowspan = rowspan
        }

        currentSubComponent = subComponentKey
        subComponentStartIndex = index
      }
    })

    // 处理最后一个子组件
    if (currentSubComponent !== null) {
      const rowspan = data.length - subComponentStartIndex
      data[subComponentStartIndex].subComponentRowspan = rowspan
    }
  }

  // 处理返回
  const handleGoBack = () => {
    router.push('/order')
  }

  // 处理编辑 - 返回到订单列表页面并打开编辑对话框
  const handleEditOrder = () => {
    // 跳转到订单列表页面，并传递编辑参数
    router.push({
      path: '/order',
      query: {
        action: 'edit',
        id: orderId.value
      }
    })
  }

  return {
    // 响应式数据
    loading,
    orderInfo,
    flattenedData,
    
    // 方法
    fetchOrderDetail,
    handleGoBack,
    handleEditOrder,
    formatDateTime,
  }
}
