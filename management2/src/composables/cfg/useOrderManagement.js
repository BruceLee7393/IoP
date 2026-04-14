// src/composables/cfg/useOrderManagement.js
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import * as orderApi from '@/api/order'

/**
 * 订单管理 UI 配置和 API 调用
 */
export function useOrderManagement() {
  const crudTableRef = ref(null)
  const router = useRouter()

  // 初始查询参数
  const initialQueryParams = {
    order_number: '',
    model: '',
    part_number: '',
    serial_number: '',
    component_part_number: '',
    sub_component_part_number: '',
  }

  // 查询字段配置
  const queryFields = [
    {
      prop: 'order_number',
      label: '订单号',
      type: 'input',
      placeholder: '请输入订单号',
      span: 6,
      props: {
        clearable: true,
      },
    },
    {
      prop: 'model',
      label: '机型',
      type: 'input',
      placeholder: '请输入机型',
      span: 6,
      props: {
        clearable: true,
      },
    },
    {
      prop: 'part_number',
      label: '料号',
      type: 'input',
      placeholder: '请输入料号',
      span: 6,
      props: {
        clearable: true,
      },
    },
    {
      prop: 'serial_number',
      label: '序列号',
      type: 'input',
      placeholder: '请输入序列号',
      span: 6,
      props: {
        clearable: true,
      },
      tooltip: '输入范围内任意序列号即可查询到所属订单',
    },
    {
      prop: 'component_part_number',
      label: '组件料号',
      type: 'input',
      placeholder: '请输入组件料号',
      span: 6,
      props: {
        clearable: true,
      },
    },
    {
      prop: 'sub_component_part_number',
      label: '子组件料号',
      type: 'input',
      placeholder: '请输入子组件料号',
      span: 6,
      props: {
        clearable: true,
      },
    },
  ]

  // 表格列配置
  const tableColumns = [
    {
      prop: 'order_number',
      label: '订单号',
      minWidth: 150,
      sortable: 'custom',
      showOverflowTooltip: true,
      slot: 'order_number', // 使用自定义模板
    },
    {
      prop: 'model',
      label: '机型',
      minWidth: 120,
      sortable: 'custom',
      showOverflowTooltip: true,
    },
    {
      prop: 'part_number',
      label: '料号',
      minWidth: 150,
      sortable: 'custom',
      showOverflowTooltip: true,
    },
    {
      prop: 'serial_range',
      label: '序列号范围',
      minWidth: 200,
      sortable: false,
      showOverflowTooltip: true,
      slot: 'serial_range', // 使用自定义模板
    },
    {
      prop: 'component_count',
      label: '组件数量',
      width: 100,
      align: 'center',
      sortable: false,
      slot: 'component_count', // 使用自定义模板
    },
    {
      prop: 'order_created_at',
      label: '生产日期',
      minWidth: 160,
      align: 'center',
      sortable: false,
      formatter: (row) => formatDateTime(row.order_created_at),
    },
    {
      prop: 'remark',
      label: '备注',
      minWidth: 150,
      sortable: false,
      showOverflowTooltip: true,
      formatter: (row) => row.remark || '-',
    },
    {
      prop: 'created_at',
      label: '创建时间',
      minWidth: 160,
      align: 'center',
      sortable: 'custom',
      formatter: (row) => formatDateTime(row.created_at),
    },
    {
      prop: 'appendix',
      label: '附件',
      width: 200,
      align: 'center',
      sortable: false,
      showOverflowTooltip: false, // 禁用默认tooltip，避免与FileUpload组件内部的文件名显示冲突
      slot: 'appendix', // 使用自定义模板
    },
  ]

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
    })
  }

  // 权限配置
  const permissions = computed(() => ({
    add: true,
    edit: true,
    delete: true,
    batchDelete: true,
    view: true,
    export: true,
  }))

  // 头部操作配置
  const headerActionConfig = {
    showAdd: true,
    showExport: true,
    showBatchDelete: true,
    customActions: [
      {
        key: 'batchImport',
        label: '批量导入',
        type: 'primary',
        icon: 'Upload',
        event: 'batchImport',
      }
    ],
  }

  // 自定义行操作配置 - 覆盖默认的详情按钮行为
  const rowActionConfig = [
    {
      key: 'view',
      label: '详情',
      type: 'primary',
      icon: 'View',
      event: 'view',
    },
    {
      key: 'edit',
      label: '修改',
      type: 'primary',
      icon: 'Edit',
      event: 'edit',
    },
    {
      key: 'delete',
      label: '删除',
      type: 'danger',
      icon: 'Delete',
      event: 'delete',
    },
  ]

  // API 调用包装
  const api = {
    // 获取订单列表
    async getList(params) {
      try {
        const response = await orderApi.getOrderList(params)
        return response
      } catch (error) {
        console.error('获取订单列表失败:', error)
        ElMessage.error('获取订单列表失败')
        throw error
      }
    },

    // 获取订单详情
    async getDetail(id) {
      try {
        const response = await orderApi.getOrderDetails(id)
        return response
      } catch (error) {
        console.error('获取订单详情失败:', error)
        throw error
      }
    },

    // 创建订单
    async create(data) {
      try {
        const result = await orderApi.createOrder(data)
        return result
      } catch (error) {
        console.error('创建订单失败:', error)
        throw error
      }
    },

    // 更新订单
    async update(id, data) {
      try {
        const result = await orderApi.updateOrder(id, data)
        return result
      } catch (error) {
        console.error('更新订单失败:', error)
        throw error
      }
    },

    // 删除订单
    async delete(id) {
      try {
        await orderApi.deleteOrder(id)
        return true
      } catch (error) {
        console.error('删除订单失败:', error)
        throw error
      }
    },

    // 批量删除订单
    async batchDelete(ids) {
      try {
        await orderApi.batchDeleteOrders(ids)
        return true
      } catch (error) {
        console.error('批量删除订单失败:', error)
        throw error
      }
    },

    // 导出订单数据
    async export(params) {
      try {
        await orderApi.exportOrders(params)
        ElMessage.success('导出请求已发送，文件将自动下载')
        return true
      } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败')
        return false
      }
    },

  }

  // 初始化数据
  const initializeData = async () => {
    try {
      // 订单管理暂时不需要初始化额外数据
      console.log('订单管理初始化完成')
    } catch (error) {
      console.error('初始化订单管理数据失败:', error)
    }
  }

  // 处理查看详情
  const handleViewDetail = (row) => {
    router.push(`/order/detail/${row.id}`)
  }

  // 自定义操作处理
  const handleCustomAction = ({ action, data }) => {
    switch (action) {
      case 'view':
      case 'detail':
        // 无论是操作栏的"详情"按钮还是其他详情操作，都跳转到详情页面
        handleViewDetail(data)
        return Promise.resolve(true)
      default:
        return Promise.resolve(false)
    }
  }

  return {
    // 响应式数据
    crudTableRef,

    // 配置
    initialQueryParams,
    queryFields,
    tableColumns,
    permissions,
    headerActionConfig,
    rowActionConfig,

    // API 调用
    api,

    // 方法
    initializeData,
    handleCustomAction,
    handleViewDetail,
  }
}


