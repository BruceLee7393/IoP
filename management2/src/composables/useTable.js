// src/composables/useTable.js
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { isNetworkError } from '@/utils/errorHandler'

export function useTable(api, options = {}) {
  const {
    initialQueryParams = {},
    autoLoad = true,
    pageSize = 10,
    onSuccess = null,
    onError = null,
    transformData = null,
    cacheKey = null,
    cacheTimeout = 5 * 60 * 1000,
  } = options

  // 响应式状态
  const loading = ref(autoLoad)
  const tableData = ref([])
  const total = ref(0)
  const selectedRows = ref([])
  const selectedIds = ref([])
  const queryParams = reactive({ ...initialQueryParams })
  const pagination = reactive({ page: 1, limit: pageSize })
  const sortParams = reactive({ prop: '', order: '' })

  // 缓存
  const cache = ref(new Map())
  const lastRequestTime = ref(0)

  /* ---------- 工具 ---------- */
  const getCacheKey = () => {
    if (!cacheKey) return null
    const params = { ...pagination, filters: { ...queryParams }, sort: { ...sortParams } }
    return `${cacheKey}_${JSON.stringify(params)}`
  }

  /* ---------- 核心：列表获取 ---------- */
  const getList = async (useCache = true, overrideParams = {}) => {
    loading.value = true
    try {
      // 1. 缓存命中
      const key = getCacheKey()
      if (useCache && key && cache.value.has(key)) {
        const cached = cache.value.get(key)
        if (Date.now() - cached.timestamp < cacheTimeout) {
          tableData.value = cached.data.records
          total.value = cached.data.total
          loading.value = false
          return cached.data
        }
      }

      // 2. 请求参数
      const params = {
        page: pagination.page,
        pageSize: pagination.limit,
        ...queryParams,
        sortBy: sortParams.prop,
        order:
          sortParams.order === 'ascending'
            ? 'asc'
            : sortParams.order === 'descending'
              ? 'desc'
              : '',
        ...overrideParams,
      }

      // 3. 获取 API 方法
      let apiMethod = null
      if (api.getList) {
        apiMethod = api.getList
      } else if (api.list) {
        apiMethod = api.list
      } else {
        throw new Error('API 对象必须包含 getList 或 list 方法')
      }

      // console.log('useTable calling API method with params:', params)
      const res = await apiMethod(params)
      // console.log('useTable received response:', res)

      // 4. 处理不同的响应格式
      let responseData
      if (res && res.data) {
        // 如果是 {data: {records: [...], total: ...}} 格式
        responseData = res.data
      } else {
        // 如果是直接的 {records: [...], total: ...} 格式
        responseData = res
      }

      // 5. 使用标准格式
      let dataSource = responseData.records || []
      let totalCount = responseData.total || 0

      // console.log('useTable 使用标准格式 - records:', dataSource.length, 'total:', totalCount)

      // 6. 外部转换钩子
      if (transformData) {
        const transformed = transformData({ records: dataSource, total: totalCount })
        dataSource = transformed.records
        totalCount = transformed.total
      }

      // 7. 写回
      tableData.value = dataSource
      total.value = totalCount
      lastRequestTime.value = Date.now()

      // 7. 缓存 & 回调
      if (key) {
        cache.value.set(key, {
          data: { records: dataSource, total: totalCount },
          timestamp: Date.now(),
        })
      }
      onSuccess?.({ list: dataSource, total: totalCount }, params)
      return { list: dataSource, total: totalCount }
    } catch (e) {
      console.error('useTable getList error:', e)
      // 网络类错误交给 http 拦截器统一提示，避免重复
      if (!isNetworkError(e)) {
        const msg = e?.msg || e?.message || '获取列表失败'
        ElMessage.error(msg)
      }
      onError?.(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  /* ---------- 其余交互逻辑 ---------- */
  const handleSearch = (searchParams) => {
    // 如果传入了搜索参数，更新查询参数
    if (searchParams) {
      Object.keys(queryParams).forEach((key) => {
        queryParams[key] = searchParams[key] ?? ''
      })
    }
    pagination.page = 1
    cache.value.clear()
    getList(false)
  }

  const handleReset = (formRef) => {
    const form = formRef?.value ?? formRef
    form?.resetFields?.()
    Object.keys(queryParams).forEach(
      (k) => (queryParams[k] = options.initialQueryParams?.[k] ?? ''),
    )
    pagination.page = 1
    sortParams.prop = ''
    sortParams.order = ''
    cache.value.clear()
    getList(false)
  }

  // 【核心修复】: 修正排序处理逻辑
  const handleSortChange = ({ prop, order }) => {
    cache.value.clear();

    if (order) {
      // 如果 order 存在 (升序或降序)，则更新排序状态并发起请求
      sortParams.prop = prop;
      sortParams.order = order;
      const sortOrder = order === 'ascending' ? 'asc' : 'desc';
      getList(false, { sortBy: prop, order: sortOrder });
    } else {
      // 如果 order 为 null (取消排序)，则清空排序状态并发起请求
      sortParams.prop = '';
      sortParams.order = '';
      // 传递 undefined 以确保这些参数不会被包含在请求中
      getList(false, { sortBy: undefined, order: undefined });
    }
  }

  const handleSelectionChange = (selection) => {
    selectedRows.value = selection
    selectedIds.value = selection.map((i) => i.id)
  }
  const handleSizeChange = (size) => {
    pagination.limit = size
    pagination.page = 1
    cache.value.clear()
    getList(false)
  }
  const handlePageChange = (page) => {
    pagination.page = page
    getList()
  }
  const clearCache = () => cache.value.clear()
  const refresh = () => {
    clearCache()
    getList(false)
  }
  const reload = () => {
    pagination.page = 1
    clearCache()
    getList(false)
  }

  /* ---------- 自动加载 ---------- */
  if (autoLoad) onMounted(() => getList())

  /* ---------- 返回 ---------- */
  return {
    loading,
    tableData,
    total,
    selectedRows,
    selectedIds,
    queryParams,
    pagination,
    sortParams,
    hasSelection: computed(() => selectedRows.value.length > 0),
    isAllSelected: computed(
      () => tableData.value.length && selectedRows.value.length === tableData.value.length,
    ),
    isIndeterminate: computed(
      () => selectedRows.value.length > 0 && selectedRows.value.length < tableData.value.length,
    ),
    getList,
    handleSearch,
    handleReset,
    handleSortChange,
    handleSelectionChange,
    handleSizeChange,
    handlePageChange,
    clearCache,
    refresh,
    reload,
  }
}
