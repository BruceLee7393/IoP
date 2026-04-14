// src/composables/useCrudTable.js
import { reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useTable } from '@/composables/useTable'
import { useCrud } from '@/composables/useCrud'
import { useStatusToggle } from '@/composables/useStatusToggle'

export function useCrudTable(props, emit) {
  // 使用Composables
  const {
    loading,
    tableData,
    total,
    selectedRows,
    selectedIds,
    queryParams,
    pagination,
    getList,
    handleSearch: baseHandleSearch, // 重命名基础函数
    handleReset: baseHandleReset,   // 重命名基础函数
    handleSortChange,
    handleSelectionChange: onSelectionChange,
    handleSizeChange,
    handlePageChange,
    clearCache,
  } = useTable(props.api, {
    initialQueryParams: props.initialQueryParams,
  })

  const { dialog, openAddDialog, openEditDialog, deleteRecord, batchDelete, submitForm } = useCrud(
    props.api,
    {
      entityName: props.entityName,
      onSuccess: () => {
        clearCache()
        getList(false)
      },
    },
  )

  const { toggleStatus } = useStatusToggle(props.api, {
    entityName: props.entityName,
    onSuccess: () => {
      clearCache()
      getList(false)
    },
  })

  // 查看对话框的响应式数据
  const viewDialog = reactive({
    visible: false,
    data: null,
  })

  // 【核心修复】: 创建新的 handleSearch 和 handleReset 函数
  const handleSearch = (searchParams) => {
    console.log('【调试 A】CrudTable 的 handleSearch 被调用，查询参数:', searchParams);
    baseHandleSearch(searchParams); // 调用 useTable 中的原始搜索逻辑
    // 【关键】: 在搜索后，手动发出 query-change 事件
    emit('query-change', queryParams);
  };
  
  const handleReset = (formRef) => {
    console.log('【调试 A】CrudTable 的 handleReset 被调用');
    baseHandleReset(formRef); // 调用 useTable 中的原始重置逻辑
    // 【关键】: 在重置后，手动发出 query-change 事件
    emit('query-change', queryParams);
  };


  // 计算属性
  const paginationWithTotal = computed(() => ({
    ...pagination,
    total: total.value,
  }))

  const tableColumns = computed(() => {
    return props.columns.map((col) => ({
      ...col,
      // 兼容性处理：如果使用key属性，转换为prop属性
      prop: col.prop || col.key,
      sortable: col.sortable !== false ? 'custom' : false,
    }))
  })

  const headerActions = computed(() => {
    const actions = []
    const config = props.headerActionConfig

    if (props.permissions.add) {
      actions.push({
        key: 'add',
        label: `添加${props.entityName}`,
        type: 'primary',
        icon: 'Plus',
        action: 'add',
        ...config.add,
      })
    }

    if (props.permissions.delete) {
      actions.push({
        key: 'batchDelete',
        label: '批量删除',
        type: 'danger',
        icon: 'Delete',
        action: 'batchDelete',
        disabled: selectedIds.value.length === 0,
        ...config.batchDelete,
      })
    }

    if (props.permissions.export) {
      actions.push({
        key: 'export',
        label: '导出',
        type: 'success',
        icon: 'Download',
        action: 'export',
        ...config.export,
      })
    }

    // 添加自定义操作
    if (config.customActions && Array.isArray(config.customActions)) {
      config.customActions.forEach((customAction) => {
        actions.push({
          key: customAction.action,
          ...customAction,
        })
      })
    }

    return actions
  })

  const rowActions = computed(() => {
    // 如果外部传入了自定义的行操作配置(rowActionConfig)，则优先使用它
    if (props.rowActionConfig && props.rowActionConfig.length > 0) {
      return props.rowActionConfig
    }

    // 否则，根据权限生成默认的行操作
    const actions = []

    if (props.permissions.view) {
      actions.push({
        key: 'view',
        label: '详情',
        type: 'primary',
        icon: 'View',
        event: 'view',
      })
    }

    if (props.permissions.edit) {
      actions.push({
        key: 'edit',
        label: '修改',
        type: 'primary',
        icon: 'Edit',
        event: 'edit',
      })
    }

    if (props.permissions.delete) {
      actions.push({
        key: 'delete',
        label: '删除',
        type: 'danger',
        icon: 'Delete',
        event: 'delete',
      })
    }

    return actions
  })

  const queryActions = computed(() => [
    {
      key: 'refresh',
      label: '刷新',
      type: 'default',
      icon: 'Refresh',
      event: 'refresh',
    },
  ])

  // 事件处理
  const handleSelectionChange = (selection) => {
    onSelectionChange(selection)
    emit('selection-change', selection)
  }

  const handleHeaderAction = async ({ action }) => {
    // 发送事件给父组件（除了export操作，因为export会在switch中直接处理）
    if (action !== 'export') {
      emit('action', { type: 'header', action, data: selectedRows.value })
    }

    switch (action) {
      case 'add':
        openAddDialog()
        break
      case 'batchDelete':
        batchDelete(selectedIds.value, () => {
          clearCache()
          getList(false)
        })
        break
      case 'export':
        {
          // 传递当前的查询参数而不是表格数据，让后端根据查询条件导出
          const exportParams = {
            ...queryParams,
            // 如果有选中的行，可以传递选中的ID列表（可选）
            selectedIds: selectedIds.value.length > 0 ? selectedIds.value : undefined,
          }
          console.log('导出参数:', exportParams)

          // 直接调用API的导出方法，避免重复触发
          if (props.api && typeof props.api.export === 'function') {
            try {
              await props.api.export(exportParams)
            } catch (error) {
              console.error('导出失败:', error)
            }
          } else {
            // 如果API中没有export方法，则发送事件给父组件处理
            emit('action', { type: 'header', action: 'export', data: exportParams })
          }
        }
        break
      default:
        emit('action', { type: 'header', action, data: selectedRows.value })
    }
  }

  const handleView = (row) => {
    viewDialog.data = { ...row }
    viewDialog.visible = true
  }

  const handleRowAction = ({ event, row }) => {
    // 首先发送事件给父组件，让父组件有机会处理自定义操作
    emit('action', { type: 'row', action: event, data: row })

    // 对于标准操作，仍然执行默认逻辑
    // 但父组件可以通过自己的handleCustomAction来覆盖这些行为
    switch (event) {
      case 'edit':
        openEditDialog(row)
        break
      case 'delete':
        deleteRecord(row, () => {
          clearCache()
          getList(false)
        })
        break
      case 'toggleStatus':
        toggleStatus(row, () => {
          clearCache()
          getList(false)
        })
        break
      case 'view':
        // 对于view操作，只有在没有自定义rowActionConfig时才执行默认行为
        if (!props.rowActionConfig || props.rowActionConfig.length === 0) {
          handleView(row)
        }
        break
      default:
        // 其他事件已经通过emit发送给父组件
        break
    }
  }

  const handleQueryAction = ({ event }) => {
    switch (event) {
      case 'refresh':
        getListWithEvent()
        break
      default:
        emit('action', { type: 'query', action: event })
    }
  }

  const handleFormSuccess = () => {
    getListWithEvent()
  }

  // 处理展开变化
  const handleExpandChange = (row, expanded) => {
    console.log('handleExpandChange called:', { row, expanded })
    emit('expand-change', row, expanded)
  }

  // 包装getList函数以发送query-change事件
  const getListWithEvent = async (useCache = true) => {
    const result = await getList(useCache)
    // 发送查询变化事件，传递当前查询参数
    const currentParams = {
      page: pagination.page,
      pageSize: pagination.limit,
      ...queryParams,
    }
    emit('query-change', currentParams)
    return result
  }

  // 更新查询参数的方法
  const updateQueryParams = (newParams) => {
    console.log('更新查询参数:', newParams)
    Object.keys(newParams).forEach((key) => {
      queryParams[key] = newParams[key]
    })
    console.log('更新后的查询参数:', queryParams)
  }



  // 生命周期
  onMounted(() => {
    getListWithEvent()
  })

  return {
    // state
    loading,
    tableData,
    queryParams,
    dialog,
    viewDialog,
    // computed
    paginationWithTotal,
    tableColumns,
    headerActions,
    rowActions,
    queryActions,
    // props
    initialQueryParams: props.initialQueryParams,
    // methods
    handleSearch,
    handleReset,
    handleQueryAction,
    handleHeaderAction,
    handleSelectionChange,
    handleSortChange,
    handleRowAction,
    handleSizeChange,
    handlePageChange,
    handleExpandChange,
    submitForm,
    handleFormSuccess,
    handleView,
    updateQueryParams,
    openAddDialog,
    openEditDialog,
  }
}